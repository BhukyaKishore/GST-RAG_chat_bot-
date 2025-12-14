# Modular RAG Application

This is a modular Retrieval-Augmented Generation (RAG) application that answers questions based on PDF documents found in the `data/` directory.

## Features
- **Models**: Uses `gpt-3.5-turbo` for generation and `text-embedding-ada-002` for embeddings.
- **Vector Database**: Uses ChromaDB for storing and retrieving document chunks.
- **Modularity**: Code is organized into logical modules (`app/core`, `app/ingestion`, `app/rag`).
- **GPU Utilization**: Chroma and LangChain will utilize GPU if available (via PyTorch/CUDA underlying libraries), though text-based RAG is often CPU-bound on ingestion/API calls.

## Prerequisites
- Python 3.9+
- OpenAI API Key

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up your environment variables:
    - Copy `.env.example` (or create `.env`) and add your OpenAI Key:
    ```bash
    OPENAI_API_KEY=sk-...
    ```

## Usage

### 1. Ingest Data
Place your PDF files in the `data/` folder. Then run:

```bash
python main.py --ingest
```
This will:
- Load PDFs from `data/`.
- Split them into chunks.
- Create/Update the Vector Store in `chroma_db/`.

### 2. Ask Questions
**Option A: Interactive CLI**
```bash
python main.py
```

**Option B: Web Interface**
```bash
uvicorn app.server:app --reload
```
Then visit `http://localhost:8000/static/index.html` in your browser.

How to Use
Activate Environment: source venv/bin/activate
Ask Questions: python main.py
Ingest New Data: Place PDFs in 
data/
and run python main.py --ingest


## Project Structure
```
.
├── app/
│   ├── config.py          # Configuration settings
│   ├── core/              # Core logic (LLM, DB setup)
│   ├── ingestion/         # Data loading and ingestion logic
│   └── rag/               # RAG chain definition
├── data/                  # PDF source files
├── main.py                # Entry point
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```
