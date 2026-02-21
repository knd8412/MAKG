from fastapi import FastAPI
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

app = FastAPI()

# --- DATABASE CONNECTION ---
MONGO_URL = "mongodb+srv://admin:SZ1kZ0HD7zmplnlq@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(MONGO_URL)
db = client.posture_hackathon

active_session = {"id": None}

@app.post("/api/button/toggle")
async def toggle_session():
    """Triggered by the physical On/Off button"""
    now = datetime.now(timezone.utc)
    if active_session["id"] is None:
        session_id = str(uuid.uuid4())[:6]
        await db.sessions.insert_one({
            "session_id": session_id, "start_time": now, "active": True, "alerts": 0
        })
        active_session["id"] = session_id
        return {"status": "started", "id": session_id}
    else:
        id_to_close = active_session["id"]
        await db.sessions.update_one({"session_id": id_to_close}, {"$set": {"active": False, "end_time": now}})
        active_session["id"] = None
        return {"status": "stopped"}

@app.post("/api/alert/bad-posture")
async def log_alert(session_id: str):
    """Triggered when the camera sees slouching"""
    await db.sessions.update_one({"session_id": session_id}, {"$inc": {"alerts": 1}})
    return {"status": "logged"}

@app.get("/api/dashboard/stats")
async def get_stats():
    """Called by the Web Manager platform"""
    cursor = db.sessions.find().sort("start_time", -1)
    return await cursor.to_list(length=10)