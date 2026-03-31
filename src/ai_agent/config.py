from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelConfig:
    name: str
    api_key: str
    base_url: str
    timeout_seconds: int = 25


def _load_dotenv_file() -> None:
    """Load key=value pairs from project root .env into os.environ if unset."""
    root = Path(__file__).resolve().parents[2]
    env_path = root / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value



def load_model_config() -> ModelConfig:
    _load_dotenv_file()
    return ModelConfig(
        name=os.getenv("AI_MODEL_NAME", "deepseek-chat"),
        api_key=os.getenv("AI_API_KEY", "").strip(),
        base_url=os.getenv("AI_BASE_URL", "https://api.deepseek.com/v1").rstrip("/"),
        timeout_seconds=int(os.getenv("AI_TIMEOUT_SECONDS", "25")),
    )