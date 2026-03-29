from __future__ import annotations

import re
from typing import Any


INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"ignore\s+all\s+instructions",
    r"system\s+prompt",
    r"developer\s+message",
    r"reveal\s+prompt",
    r"输出系统提示词",
    r"忽略以上",
    r"越狱",
    r"jailbreak",
    r"api\s*key",
]

INJECTION_REGEX = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)


def looks_like_injection(text: str) -> bool:
    if not text:
        return False
    return bool(INJECTION_REGEX.search(text))


def sanitize_text(text: Any, max_len: int = 1200) -> str:
    value = str(text or "")
    value = value.replace("\x00", " ")
    value = re.sub(r"[\r\n\t]+", " ", value)
    value = re.sub(r"\s{2,}", " ", value).strip()
    if len(value) > max_len:
        value = value[:max_len] + "..."
    return value


def sanitize_string_list(values: list[Any], item_max_len: int = 80, max_items: int = 20) -> list[str]:
    cleaned: list[str] = []
    for item in values[:max_items]:
        text = sanitize_text(item, max_len=item_max_len)
        if text:
            cleaned.append(text)
    return cleaned


def build_injection_flags(*texts: str) -> list[str]:
    flags: list[str] = []
    for idx, text in enumerate(texts, start=1):
        if looks_like_injection(text):
            flags.append(f"input_{idx}_suspicious")
    return flags
