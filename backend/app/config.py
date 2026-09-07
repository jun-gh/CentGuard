"""Central place for environment-driven settings."""
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./centwhisper.db")

if not ANTHROPIC_API_KEY:
    # Don't crash on import (e.g. during `python run_seed.py`), but warn loudly.
    print(
        "[CentWhisper] WARNING: ANTHROPIC_API_KEY is not set. "
        "Copy .env.example to .env and add your key before running the chat API."
    )
