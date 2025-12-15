# TaxBuddy AI Assistant

TaxBuddy is a Retrieval-Augmented Generation (RAG) application designed to assist with GST and Income Tax queries. It uses OpenAI's models to answer questions based on documents stored in the `data/` directory.

## Features

- **Interactive Web Interface**: A modern, responsive chat UI (`TaxBuddy`) with dark mode support.
- **RAG Powered**: Retrieves relevant context from your PDF documents to answer questions accurately.
- **Persistent Chat History**: Chats are saved as JSON files in `chat_sessions/`, allowing you to revisit conversations.
- **Image Upload**: (Mock) Support for uploading images in the chat.
- **Modular Design**: organized codebase into `app/` (core logic), `frontend/` (UI), and `data/` (knowledge base).

## Project Structure

```
.
├── app/
│   ├── server.py          # FastAPI Web Server (Entry Point)
│   ├── core/              # Configuration & DB connection
│   ├── ingestion/         # Document processing logic
│   └── rag/               # LangChain RAG pipeline definition
├── frontend/
│   └── index.html         # Main Chat UI (HTML/JS/CSS)
├── data/                  # Place your PDF documents here
├── chat_sessions/         # Stores chat history (JSON files)
├── chroma_db/             # Vector Database storage
└── requirements.txt       # Python dependencies
```

## Setup & Installation

1.  **Clone the repository**
2.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Environment Variables**:
    Create a `.env` file in the root directory and add your OpenAI API Key:
    ```bash
    OPENAI_API_KEY=sk-...
    ```

## Usage

### 1. Ingest Data (Prepare Knowledge Base)
Before asking questions, you need to process your PDF files. Place them in `data/` and run:

```bash
python main.py --ingest
```

### 2. Run the Web Server (Recommended)
This starts the TaxBuddy web interface.

```bash
./venv/bin/uvicorn app.server:app --port 8000 --host 0.0.0.0
# OR
python -m uvicorn app.server:app --port 8000
```

Open your browser and navigate to: **http://localhost:8000**

### 3. Run CLI (Alternative)
You can also chat via the terminal:

```bash
python main.py
```

## Key Files Documentation

- **`app/server.py`**: The web server. Handles API routes for chat (`/chat`), history loading (`/load_chat`), and session management (`/new_chat`).
- **`app/rag/chain.py`**: Defines the RAG chain using LangChain. It combines retrieval (from ChromaDB) with the LLM to generate answers.
- **`frontend/index.html`**: The complete frontend application. Contains the HTML structure, CSS styling, and JavaScript logic for communicating with the backend APIs.

## Troubleshooting

- **500 Error / Authentication Error**: Ensure your `OPENAI_API_KEY` in `.env` is correct.
- **No Answers**: Make sure you have run the ingestion step (`python main.py --ingest`) so the database has content.
