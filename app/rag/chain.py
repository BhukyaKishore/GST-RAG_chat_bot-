"""
This module defines the Retrieval-Augmented Generation (RAG) chain.

It combines:
1. A Language Model (LLM).
2. A Vector Database (ChromaDB) for retrieval.
3. Conversational Memory to handle follow-up questions.

Key components:
- build_rag_chain(): The main function that assembles the pipeline.
- get_session_history(): Manages in-memory chat history for the chain (note: server also saves to disk).
"""
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from app.core.models import get_llm
from app.core.db import get_vectorstore

# Global store for session histories
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def build_rag_chain():
    """Builds and returns the RAG chain with history-aware retrieval."""
    llm = get_llm()
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # 1. Contextualize Question Chain
    # Rephrase the question based on history to make it standalone
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # 2. Answer Question Chain (QA)
    qa_system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If the user's question is about the conversation history "
        "(e.g. 'what did I just ask', 'summarize our chat'), "
        "answer it using the provided chat history. "
        "If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # 3. Combine History Retrieval + QA
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # Trim history to last 5 messages
    def trim_messages(chain_input):
        if "chat_history" in chain_input:
            chain_input["chat_history"] = chain_input["chat_history"][-5:]
        return chain_input

    chain_with_trimming = RunnablePassthrough(trim_messages) | rag_chain

    conversational_rag_chain = RunnableWithMessageHistory(
        chain_with_trimming,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return conversational_rag_chain
