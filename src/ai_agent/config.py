from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    name: str
    api_key: str
    base_url: str
    timeout_seconds: int = 25



def load_model_config() -> ModelConfig:
    return ModelConfig(
        name=os.getenv("AI_MODEL_NAME", "deepseek-chat"),
        # api_key=os.getenv("AI_API_KEY", "").strip(),
        api_key="sk-8cda261b605641619e7ada6a0ad3261f",
        # 调试阶段暂时显性写入，正式环境请务必使用环境变量或安全存储方式
        base_url=os.getenv("AI_BASE_URL", "https://api.deepseek.com/v1").rstrip("/"),
        timeout_seconds=int(os.getenv("AI_TIMEOUT_SECONDS", "25")),
    )