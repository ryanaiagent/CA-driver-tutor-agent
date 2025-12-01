import asyncio
import uuid
import sys
import logging
import os
import warnings

# Ensure Python can find your agent.py file
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ADK Imports
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types 

# Import your agent definition
from agent import root_agent

# ==========================================
# 1. CLEAN LOGGING & WARNINGS
# ==========================================
# Hide the "Quota Project" warning
warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

# Configure Logging (Hide noisy internal logs)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Orchestrator")

# Silence libraries
logging.getLogger("google_adk").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("googleapiclient").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def make_content(text_input: str) -> types.Content:
    """Wraps text in the specific object structure required by the Runner."""
    return types.Content(
        role="user", 
        parts=[types.Part(text=text_input)]
    )

def print_clean_response(event):
    """
    Intelligently extracts and prints ONLY the text from the agent response,
    hiding the raw object structure and thought signatures.
    """
    if not event.content:
        return

    # Case A: It's just a string (Simple)
    if isinstance(event.content, str):
        print(event.content, end="", flush=True)
        return

    # Case B: It's a GenAI Content Object (Complex)
    # This fixes the "parts=[Part(text=...)]" issue
    if hasattr(event.content, 'parts'):
        for part in event.content.parts:
            # We only print text parts, ignoring function calls/thoughts if mixed in
            if part.text:
                print(part.text, end="", flush=True)


# ==========================================
# 3. MAIN ORCHESTRATOR
# ==========================================
async def main():
    print("\n🚗 Initializing California Driver's Prep Agent...")

    # Initialize Memory
    session_service = InMemorySessionService()
    user_id = "hackathon-judge-1"
    session_id = str(uuid.uuid4())
    app_name = "driver-prep-app"

    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    # Initialize Runner
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=app_name
    )

    print("="*60)
    
    # --- AUTO-START (Wake Up Call) ---
    try:
        startup_msg = make_content(
            "System: Begin session. Introduce yourself exactly as defined in PHASE 1 of your instructions."
        )
        
        print("\033[92mTutor:\033[0m ", end="", flush=True) 
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=startup_msg
        ):
            print_clean_response(event)  # <--- Using the new helper
            
        print("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Startup Error: {e}")

    # --- INTERACTION LOOP ---
    while True:
        try:
            user_input = input("\n\033[94mYou:\033[0m ") # Blue Text
            
            if user_input.lower() in ['exit', 'quit']:
                print("\033[92mTutor:\033[0m Good luck on your test!")
                break

            msg_obj = make_content(user_input)

            print("\033[92mTutor:\033[0m ", end="", flush=True) 
            
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=msg_obj
            ):
                print_clean_response(event) # <--- Using the new helper
            
            print("") 

        except Exception as e:
            logger.error(f"Runtime Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())