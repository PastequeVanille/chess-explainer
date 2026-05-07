from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    stockfish_path: str | None
    wikibooks_user_agent: str


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5"),
        stockfish_path=os.getenv("STOCKFISH_PATH"),
        wikibooks_user_agent=os.getenv(
            "WIKIBOOKS_USER_AGENT",
            "ChessExplainer/0.1 (educational chess project; contact: example@example.com)",
        ),
    )
