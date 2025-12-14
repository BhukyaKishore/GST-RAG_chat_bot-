# Project Explanation & Architecture

This document explains the internal working of the Modular RAG Application, detailing the flow of data, key components, and the reasoning behind specific implementation choices.

## 1. High-Level Overview

This application is a **Retrieval-Augmented Generation (RAG)** system.
*   **Goal**: Answer user questions based on private PDF documents (like GST regulations) while maintaining conversation history.
*   **Tech Stack**:
    *   **LangChain**: Orchestrates the AI components.
    *   **OpenAI**: Provides the LLM (`gpt-3.5-turbo`) and Embeddings (`text-embedding-ada-002`).
    *   **ChromaDB**: A vector database to store and retrieve document chunks based on semantic similarity.
    *   **FastAPI**: Serves the application as a web API.
    *   **Vanilla JS/HTML**: Provides a simple chat interface.

---

## 2. Architecture Flow

The application works in two main phases: **Ingestion** (Preparation) and **Querying** (Runtime).

### Phase 1: Ingestion (`app/ingestion/ingest.py`)
Before we can answer questions, we must process the documents.

1.  **Loading**: `PyPDFLoader` reads raw PDF files from the `data/` folder.
2.  **Splitting**: One large PDF is too big for an LLM context window. We use `RecursiveCharacterTextSplitter` to chop it into smaller chunks (e.g., 1000 characters). allowing overlap (200 chars) to maintain context across boundaries.
3.  **Embedding & Storage**: Each chunk is converted into a list of numbers (vector) using OpenAI Embeddings. These vectors are saved in **ChromaDB**. Semantic search works by finding vectors close to each other.

### Phase 2: Querying (`app/rag/chain.py` & `app/server.py`)
When a user asks a question via the frontend:

1.  **Session Management**: The server receives a `session_id`. It loads the specific chat history for that user.
2.  **History-Aware Retrieval**:
    *   *Problem*: If a user asks "What are its benefits?", the system doesn't know what "its" refers to.
    *   *Solution*: We use a `create_history_aware_retriever`. It takes the chat history + latest question and asks the LLM to rewrite it into a **standalone question** (e.g., "What are the benefits of GST?").
3.  **Retrieval**: This standalone question is used to search ChromaDB for the most relevant document chunks.
4.  **Generation**: The LLM receives the **Retrieved Context**, the **Chat History**, and the **User's Question**. It generates a final answer.
5.  **Memory Update**: The question and answer are saved to the `ChatMessageHistory` for the next turn.

---

## 3. Code Deep Dive

### A. The RAG Chain (`app/rag/chain.py`)
This is the heart of the logic.

```python
# 1. Reformulate Question
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question... "
    "formulate a standalone question..."
)
history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
```
*   **Why?**: To handle follow-up questions like "Why?" or "Explain more".

```python
# 2. Answer Question
qa_system_prompt = (
    "Use the following pieces of retrieved context to answer... "
    "If the user's question is about the conversation history... "
    "answer it using the provided chat history."
)
```
*   **Why?**: The prompt was updated to handle meta-questions like "What did I just ask?". Standard RAG prompts often forbid using anything outside the retrieved text, which breaks "chat about chat" functionality.

```python
# 3. Memory Window
def trim_messages(chain_input):
    if "chat_history" in chain_input:
        chain_input["chat_history"] = chain_input["chat_history"][-5:]
    return chain_input
```
*   **Why?**: LLMs have a token limit. If we send the entire history of a 100-message chat, it will crash or cost too much. We only keep the last 5 interactions.

### B. The Server (`app/server.py`)
```python
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    response = rag_chain.invoke(
        {"input": request.message},
        config={"configurable": {"session_id": session_id}}
    )
```
*   **Why?**: Used `RunnableWithMessageHistory`. The `config` dictionary is how LangChain knows which memory object to retrieve from the global store.

---

## 4. Why Modular?
Instead of one giant `main.py`, we split it:
*   `app/core`: Singleton objects (DB, LLM) reused everywhere. Prevents re-initializing connections.
*   `app/ingestion`: Separate because ingestion happens *once*, while querying happens *often*.
*   `app/rag`: Contains the "business logic" of the AI.

This structure allows us to easily swap out components (e.g., change Chroma to Pinecone, or OpenAI to Ollama) without rewriting the whole app.
