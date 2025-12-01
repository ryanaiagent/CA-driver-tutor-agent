# 🚗 California Driver's Prep Agent

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