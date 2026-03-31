from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_agent.api.routes import router as ai_router
from ai_agent.resume.router import router as resume_router


app = FastAPI(title="Job Info Collector AI Agent", version="0.1.0-mvp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "ai-agent", "status": "ok"}


app.include_router(ai_router)
app.include_router(resume_router)
