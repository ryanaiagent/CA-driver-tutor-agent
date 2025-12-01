# 🚗 California Driver's Tutor Agent

> **A Multi-Agent System powered by Google ADK, Vertex AI Agent Engine, and RAG.**

This agent acts as an intelligent **Driving Exam Tutor**. It doesn't just chat; it follows a strict pedagogical protocol to teach the California Driver's Handbook, conduct adaptive quizzes, and provide visual video aids.

---

## 🌟 Key Features

*   **📚 RAG (Retrieval Augmented Generation):** Uses **Vertex AI Vector Search** to fetch "Source of Truth" answers directly from the official California Driver's Handbook PDF.
*   **🧠 Multi-Agent Architecture:**
    *   **Root Agent (Tutor):** Manages the session, quiz logic, and user interaction.
    *   **Sub-Agent (Researcher):** specialized in RAG retrieval to ensure factual accuracy.
*   **🎥 Visual Learning (YouTube API):** Detects when a user is struggling with physical maneuvers (e.g., Parallel Parking) and automatically fetches instructional videos.
*   **📊 State Management:** Tracks quiz scores and "Batch Logic" (e.g., sets of 5 questions) using in-memory session persistence.

---
###  Technical Architecture
The project leverages the **Vertex AI Agent Engine** and the **Google ADK** to orchestrate a robust Agent-to-Agent (A2A) workflow.

**A. Architecture Diagram**

![A diagram showing the multi-agent architecture with RAG and YouTube tools.](https://github.com/ryanaiagent/CA-driver-tutor-agent/blob/main/CA_driver_tutor_agent/assets/Architectural%20diagram.png)

**B. Multi-Agent Design (The "Agent Tool" Pattern)**
To ensure accuracy, I separated the system into two distinct agents...


## 🛠️ Tech Stack

*   **Framework:** [Google Agent Development Kit (ADK)](https://github.com/google/google-adk)
*   **Model:** Gemini 2.5 Flash (via Vertex AI)
*   **Orchestration:** Python & ADK Runner
*   **Tools:**
    *   `google-api-python-client` (YouTube)
    *   `vertexai.preview.rag` (Knowledge Base)

---

## 🚀 Setup & Installation

### 1. Prerequisites
*   Python 3.12+
*   Google Cloud Project with Vertex AI API enabled.
*   A Vertex AI RAG Corpus (California Handbook PDF indexed).
*   A Youtube data api key

### 2. Install uv (if not installed)
pip install uv\
Create and activate\
uv venv --python 3.12\
source .venv/bin/activate

### 3. Install Dependencies
* Install the required Python libraries from requirements.txt

### 4.Configure Environment
This project uses a .env file to manage secrets.\
Create a file named .env in the root directory.\
Copy and paste the following configuration:\

Google Cloud Configuration\
GOOGLE_CLOUD_PROJECT=your-project-id-here\
GOOGLE_CLOUD_REGION=your-location\

Vertex AI RAG Corpus ID\
Format: projects/{PROJECT_NUMBER}/locations/{REGION}/ragCorpora/{CORPUS_ID}\
eg: RAG_CORPUS_NAME=projects/123456789/locations/your-location/ragCorpora/987654321

* YouTube Data API Key (For video search tool)
YOUTUBE_API_KEY=Your Key Here

---

* ## Usage
Once the environment is configured, run the main orchestrator script:

python3 main.py
* ## What to Expect:
* The agent will initialize and connect to Vertex AI.
* It will automatically "Wake Up" and introduce itself:\
"I am your Driving Exam Tutor. I can help you study by explaining specific rules, finding instructional videos, or taking a practice quiz."
* You can type quiz to start a practice session, or ask questions directly (e.g., "How do I parallel park?").
* Type exit or quit to stop the session.

* ## Demo Script (For Judges)
Follow this flow to demonstrate all capabilities:

*  The Setup\
Tutor: "I am your Driving Exam Tutor... How would you like to proceed?" \
You: "I want to take a quiz."\
Tutor: "How many questions?"\
You: "3"\
Tutor: "What topic?"\
You: "Parking rules."\

*  The RAG & Logic\
Tutor: (Asks a specific question about colored curbs based on the PDF).\
You: (Answer correctly).\
Tutor: (Confirms and tracks score).\

*  The Visual Aid (YouTube)\
Tutor: (Asks about Parallel Parking).\
You: "I honestly don't understand how to do that."\
Tutor: (Detects confusion -> Calls YouTube Tool -> Displays video link).\

*  The Completion\
You: (Finish the 3rd question).\
Tutor: "Batch Complete. Your score is 3/3. Would you like to start the next set?"

---
* ## Project Structure
```text
kaggle-driver-agent/
├── .env               # API Keys (Excluded from Git)
├── .gitignore         # Tells Git which files to ignore
├── agent.py           # Core Logic: Agent definitions, Tools, and Config
├── main.py            # Orchestrator: Async Runner loop & Event Handling
├── rag_prompt.txt     # System Prompt for the RAG Sub-Agent
├── root_prompt.txt    # System Prompt for the Main Tutor Agent
├── requirements.txt   # List of Python dependencies
└── README.md          # Project Documentation
```