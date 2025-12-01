"""
California Driver's License Tutor Agent.
"""
import logging
import os
import sys
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import vertexai
from vertexai.preview import rag
from google.genai import types

# ADK Imports
from google.adk.agents import LlmAgent  
from google.adk.models import Gemini
from google.adk.tools import AgentTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Config:
    """Configuration handler."""
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
    LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
    RAG_CORPUS_NAME = os.getenv("RAG_CORPUS_NAME")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

    @classmethod
    def validate(cls) -> None:
        if not cls.PROJECT_ID or not cls.RAG_CORPUS_NAME:
            raise ValueError("Missing critical environment variables (PROJECT_ID or RAG_CORPUS_NAME).")

# Initialize Vertex AI
try:
    Config.validate()
    logger.info(f"Initializing Vertex AI in {Config.LOCATION}...")
    vertexai.init(project=Config.PROJECT_ID, location=Config.LOCATION)
except Exception as e:
    logger.critical(f"Initialization failed: {e}")
    sys.exit(1)


# ==========================================
# HELPER: READ PROMPTS
# ==========================================
def load_prompt(filename: str) -> str:
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, filename)
        
        with open(full_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Prompt file {filename} not found at {full_path}.")
        return "You are a helpful assistant."


# ==========================================
# GLOBAL STATE (Hackathon Simple Memory)
# ==========================================
SESSION_SCORE = {
    "correct": 0, 
    "total": 0, 
    "history": [], 
    "limit": 0,        
    "batch_count": 0   
}


# ==========================================
# TOOL DEFINITIONS
# ==========================================
def set_quiz_limit(number: int) -> str:
    """
    Sets the number of questions for the current quiz session.
    """
    try:
        limit = int(number)
    except:
        return "Error: Please provide a valid number."
        
    SESSION_SCORE['limit'] = limit
    SESSION_SCORE['batch_count'] = 0  
    
    logger.info(f"Quiz Limit set to {limit}")
    return f"Quiz configured for {limit} questions. Ask for the topic and start Question 1."

def record_quiz_result(outcome: str, topic: str) -> str:
    """
    Records the result and tells the agent if the batch is done.
    """
    clean_outcome = outcome.lower().strip()
    SESSION_SCORE["total"] += 1
    SESSION_SCORE["batch_count"] += 1 
    
    if clean_outcome == "correct":
        SESSION_SCORE["correct"] += 1
    
    SESSION_SCORE["history"].append(f"{topic}: {clean_outcome}")
    
    current_score = SESSION_SCORE["correct"]
    total_score = SESSION_SCORE["total"]
    
    # --- BATCH LOGIC ---
    limit = SESSION_SCORE['limit']
    current_batch = SESSION_SCORE['batch_count']
    
    msg = f"Result recorded ({clean_outcome}). Total Score: {current_score}/{total_score}. "
    
    if limit > 0:
        if current_batch >= limit:
            # Batch is finished
            SESSION_SCORE['batch_count'] = 0 
            return msg + f"BATCH COMPLETE ({limit}/{limit}). Stop giving questions. Summary: {current_score}/{total_score}. Ask to continue."
        else:
            # Batch continues
            return msg + f"Progress: {current_batch}/{limit}. Proceed to next question."
            
    return msg + "Proceed."

def record_quiz_result(outcome: str, topic: str) -> str:
    """
    Records the user's success/failure on a question.
    Call this immediately after evaluating the user's answer.

    Args:
        outcome: 'correct' or 'incorrect'.
        topic: The subject of the question (e.g., 'Parking').
    """
    clean_outcome = outcome.lower().strip()
    SESSION_SCORE["total"] += 1
    
    if clean_outcome == "correct":
        SESSION_SCORE["correct"] += 1
    
    SESSION_SCORE["history"].append(f"{topic}: {clean_outcome}")
    
    current = SESSION_SCORE["correct"]
    total = SESSION_SCORE["total"]
    
    logger.info(f"📝 Score Updated: {current}/{total} ({topic}: {clean_outcome})")
    
    return f"Result recorded. Current Score: {current}/{total}."

def find_instructional_video(topic: str) -> str:
    """
    Searches YouTube for an instructional video on a driving topic.
    """
    logger.info(f"Searching YouTube for topic: {topic}")

    if not Config.YOUTUBE_API_KEY:
        return "Video tool unavailable (Missing API Key)."

    try:
        youtube = build("youtube", "v3", developerKey=Config.YOUTUBE_API_KEY)
        search_query = f"how to {topic} california dmv driving test"
        
        request = youtube.search().list(
            part="snippet", maxResults=1, q=search_query, type="video", videoDuration="medium"
        )
        response = request.execute()
        items = response.get("items", [])
        
        if not items:
            return f"No videos found for '{topic}'."

        video = items[0]
        title = video["snippet"]["title"]
        vid_id = video["id"]["videoId"]
        thumb = video["snippet"]["thumbnails"]["high"]["url"]
        
        return (
            f"I found a video for **{topic}**:\n\n"
            f"**{title}**\n"
            f"[![Watch Video]({thumb})](https://www.youtube.com/watch?v={vid_id})"
        )

    except Exception as e:
        logger.error(f"YouTube Error: {e}")
        return "Error searching YouTube."

def search_handbook(query: str) -> str:
    """
    Searches the California Driver's Handbook via Vertex AI RAG.
    """
    logger.info(f"Querying RAG Corpus for: '{query}'")
    try:
        response = rag.retrieval_query(
            rag_resources=[rag.RagResource(rag_corpus=Config.RAG_CORPUS_NAME)],
            text=query,
            similarity_top_k=7
        )
        
        # Handle Vertex SDK response structure
        # Check if contexts exist and are not empty
        if hasattr(response, 'contexts') and hasattr(response.contexts, 'contexts'):
             # New SDK Structure
             ctx_list = response.contexts.contexts
        elif hasattr(response, 'contexts'):
             # Older SDK or different structure
             ctx_list = response.contexts
        else:
             ctx_list = []

        if not ctx_list:
            return "No information found in the handbook."
            
        facts = "FACTS FROM HANDBOOK:\n"
        for item in ctx_list:
            facts += f"- {item.text}\n"
        return facts

    except Exception as e:
        logger.error(f"RAG Error: {e}")
        return f"Error accessing handbook: {e}"


# ==========================================
# AGENT DEFINITIONS
# ==========================================

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

gemini_model = Gemini(model_name="gemini-2.5-flash",retry_options=retry_config)

# 1. RAG Sub-Agent
rag_agent = LlmAgent(
    name="cali_driver_researcher",
    model=gemini_model,
    tools=[search_handbook],
    instruction=load_prompt("rag_prompt.txt")
)

# 2. Root Agent
root_agent = LlmAgent(
    name="driving_tutor",
    model=gemini_model,
    tools=[
        find_instructional_video,
        record_quiz_result,
        set_quiz_limit,
        record_quiz_result,     
        AgentTool(agent=rag_agent) 
    ],
    instruction=load_prompt("root_prompt.txt")
)