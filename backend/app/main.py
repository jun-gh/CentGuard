from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import chat, spending


# Make sure tables exist even if someone forgot to run run_seed.py first.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CentWhisper API",
    description="Personal finance copilot backend — Claude + MCP + FastAPI.",
    version="0.1.0",
)

# Wide-open CORS for local dev / demo purposes. Tighten this before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(spending.router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "CentWhisper API"}
