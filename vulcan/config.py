"""Runtime configuration.

Everything speaks to one OpenAI-compatible endpoint, so the same code runs
against Ollama on a laptop and vLLM on a ROCm box. Only the env changes.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    base_url: str = field(default_factory=lambda: os.getenv("VULCAN_BASE_URL", "http://localhost:11434/v1"))
    api_key: str = field(default_factory=lambda: os.getenv("VULCAN_API_KEY", "local"))
    model: str = field(default_factory=lambda: os.getenv("VULCAN_MODEL", "qwen3:8b"))
    embed_model: str = field(default_factory=lambda: os.getenv("VULCAN_EMBED_MODEL", "nomic-embed-text"))
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("VULCAN_DATA_DIR", "~/.vulcan")).expanduser())
    max_steps: int = int(os.getenv("VULCAN_MAX_STEPS", "12"))
    temperature: float = float(os.getenv("VULCAN_TEMPERATURE", "0.2"))

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)


def load() -> Config:
    return Config()
