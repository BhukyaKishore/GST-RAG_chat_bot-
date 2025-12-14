from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.rag.chain import build_rag_chain
from langchain_core.messages import HumanMessage
import uuid
import uvicorn
import os

app = FastAPI()

# Mount frontend directory
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
if not os.path.exists(frontend_path):
    os.makedirs(frontend_path)

app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Initialize Chain
rag_chain = build_rag_chain()

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        response = rag_chain.invoke(
            {"input": request.message},
            config={"configurable": {"session_id": session_id}}
        )
        return {
            "answer": response["answer"],
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Go to /static/index.html to use the chat interface"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
