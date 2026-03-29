from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HRSessionState:
    session_id: str
    turns: int = 0
    # Stored as simple strings/lists to keep serialization easy.
    education: str = ""
    major: str = ""
    grade: str = ""
    skills: list[str] = field(default_factory=list)
    experience_summary: str = ""
    city_preferences: list[str] = field(default_factory=list)
    industry_preferences: list[str] = field(default_factory=list)
    intent: str = ""
    recruit_type: str = ""
    job_category: str = ""
    city: str = ""
    summary: str = ""
    history: list[dict[str, str]] = field(default_factory=list)


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, HRSessionState] = {}

    def get(self, session_id: str) -> HRSessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = HRSessionState(session_id=session_id)
        return self._sessions[session_id]

    def reset(self, session_id: str) -> None:
        self._sessions[session_id] = HRSessionState(session_id=session_id)
