from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.rag.chain import build_rag_chain
import os
import uuid
import json
from datetime import datetime
import traceback

app = FastAPI()

frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
if not os.path.exists(frontend_path):
    os.makedirs(frontend_path)

app.mount("/static", StaticFiles(directory=frontend_path), name="static")
templates = Jinja2Templates(directory=frontend_path)

CHAT_DIR = "chat_sessions"
INDEX_FILE = os.path.join(CHAT_DIR, "index.json")

os.makedirs(CHAT_DIR, exist_ok=True)

# Initialize Chain
rag_chain = build_rag_chain()

def answer_question(user_msg, session_id):
    try:
        response = rag_chain.invoke(
            {"input": user_msg},
            config={"configurable": {"session_id": session_id}}
        )
        return response["answer"]
    except Exception as e:
        print(f"Error generating answer: {e}")
        traceback.print_exc()
        return "I encountered an error processing your request. Please check technical logs."

# ---------- Helpers ----------
def index_load():
    if not os.path.exists(INDEX_FILE):
        return []
    try:
        with open(INDEX_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def index_save(data):
    with open(INDEX_FILE, "w") as f:
        json.dump(data, f, indent=4)


def chat_file(cid):
    return os.path.join(CHAT_DIR, f"{cid}.json")


def load_history(cid):
    file = chat_file(cid)
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return []


def save_history(cid, history):
    with open(chat_file(cid), "w") as f:
        json.dump(history, f, indent=4)


# ---------- ROUTES ----------
@app.post("/delete_chat")
async def delete_chat(request: Request):
    data = await request.json()
    cid = data["conversation_id"]

    # Delete chat JSON file
    file_path = chat_file(cid)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Remove from index.json
    chats = index_load()
    chats = [c for c in chats if c["id"] != cid]
    index_save(chats)

    return JSONResponse({"status": "deleted"})


@app.get("/")
async def home(request: Request):
    chats = index_load()
    cid = str(uuid.uuid4())
    # Create empty history file for new session if accessing root
    save_history(cid, [])
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "conversation_id": cid,
            "chats": chats
        }
    )


@app.post("/new_chat")
async def new_chat():
    cid = str(uuid.uuid4())

    entry = {
        "id": cid,
        "title": "New Chat",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    chats = index_load()
    chats.insert(0, entry)
    index_save(chats)

    save_history(cid, [])

    return JSONResponse({"conversation_id": cid})


@app.post("/load_chat")
async def load_chat(request: Request):
    data = await request.json()
    cid = data["conversation_id"]

    history = load_history(cid)
    return JSONResponse({"history": history})


@app.post("/chat")
async def chat_api(request: Request):
    data = await request.json()

    cid = data["conversation_id"]
    user_msg = data["message"]

    history = load_history(cid)
    history.append({"role": "user", "content": user_msg})
    save_history(cid, history) # Save user message first

    bot_reply = answer_question(user_msg, cid)
    history.append({"role": "assistant", "content": bot_reply})

    save_history(cid, history)

    # Update title to first user message if needed
    chats = index_load()
    updated = False
    for chat in chats:
        if chat["id"] == cid:
            if chat["title"] == "New Chat":
                chat["title"] = user_msg[:40]
                updated = True
                break # Only update first match
    
    # If this is a fresh chat not in index (e.g. from direct URL), add it
    if not any(c['id'] == cid for c in chats):
         entry = {
            "id": cid,
            "title": user_msg[:40],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
         chats.insert(0, entry)
         updated = True

    if updated:
        index_save(chats)

    return JSONResponse({"reply": bot_reply})

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    # Mock implementation
    return {"summary": f"Image '{file.filename}' received. Image processing not implemented (files persisted only)."}

@app.post("/clear_chat")
async def clear_chat(request: Request):
    data = await request.json()
    cid = data["conversation_id"]
    save_history(cid, [])

    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
