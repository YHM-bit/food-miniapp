import os, json, re, hmac, hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import parse_qsl
from typing import Dict, Any, List, Optional
from threading import Lock

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse

TZ = ZoneInfo("Europe/Uzhgorod")
DB_PATH = "db.json"

BOT_TOKEN = os.environ.get("BOT_TOKEN")
AI_API_KEY = os.environ.get("AI_API_KEY")
AI_ENDPOINT = os.environ.get("AI_ENDPOINT", "https://models.github.ai/inference")
AI_MODEL = os.environ.get("AI_MODEL", "openai/gpt-4o-mini")

if not BOT_TOKEN:
    raise RuntimeError("Set BOT_TOKEN env var.")
if not AI_API_KEY:
    raise RuntimeError("Set AI_API_KEY env var.")

LOCK = Lock()
app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True, "files": {
        "web/index.html": os.path.exists("web/index.html"),
        "index.html": os.path.exists("index.html"),
    }}

@app.get("/", response_class=HTMLResponse)
def root():
    
    if os.path.exists("web/index.html"):
        return FileResponse("web/index.html")
    
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    
    return HTMLResponse(
        "<h2>index.html not found</h2>"
        "<p>Expected: web/index.html or index.html</p>",
        status_code=500
    )
