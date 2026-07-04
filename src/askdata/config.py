"""Central settings, read from environment / .env."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "askdata.duckdb"


@dataclass
class Settings:
    provider: str = field(default_factory=lambda: os.getenv("ASKDATA_PROVIDER", "auto"))
    anthropic_model: str = field(
        default_factory=lambda: os.getenv("ASKDATA_ANTHROPIC_MODEL", "claude-sonnet-5")
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("ASKDATA_OPENAI_MODEL", "gpt-4o-mini")
    )
    ollama_model: str = field(
        default_factory=lambda: os.getenv("ASKDATA_OLLAMA_MODEL", "qwen2.5-coder:7b")
    )
    gemini_model: str = field(
        default_factory=lambda: os.getenv("ASKDATA_GEMINI_MODEL", "gemini-2.5-flash")
    )
    groq_model: str = field(
        default_factory=lambda: os.getenv("ASKDATA_GROQ_MODEL", "llama-3.3-70b-versatile")
    )
    db_path: Path = field(
        default_factory=lambda: Path(os.getenv("ASKDATA_DB", str(DEFAULT_DB_PATH)))
    )
    max_attempts: int = field(default_factory=lambda: int(os.getenv("ASKDATA_MAX_ATTEMPTS", "3")))
    row_limit: int = field(default_factory=lambda: int(os.getenv("ASKDATA_ROW_LIMIT", "500")))

    def resolved_provider(self) -> str:
        if self.provider != "auto":
            return self.provider
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        raise RuntimeError(
            "No LLM provider configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY "
            "(see .env.example), or pass an explicit client for testing."
        )
