from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import chat, spending
from app.seed_data import seed

# Make sure tables exist even if someone forgot to run run_seed.py first.
Base.metadata.create_all(bind=engine)

# Auto-seed on startup if the DB is empty. This matters especially on Render's
# free tier, where the filesystem resets on every redeploy and there's no
# shell access to run `python run_seed.py` manually.
seed()

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
