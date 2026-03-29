from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ai_agent.config import ModelConfig, load_model_config


class LLMClient:
    def __init__(self, config: ModelConfig | None = None) -> None:
        self.config = config or load_model_config()

    @property
    def enabled(self) -> bool:
        return bool(self.config.api_key)

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2, max_tokens: int = 600) -> str:
        if not self.enabled:
            return ""

        url = f"{self.config.base_url}/chat/completions"
        payload = {
            "model": self.config.name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = Request(
            url=url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
            },
        )

        try:
            with urlopen(req, timeout=self.config.timeout_seconds) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
        except (HTTPError, URLError, TimeoutError):
            return ""

        try:
            parsed: dict[str, Any] = json.loads(body)
            choices = parsed.get("choices", [])
            if not choices:
                return ""
            message = choices[0].get("message", {})
            content = str(message.get("content", "")).strip()
            return content
        except Exception:
            return ""
