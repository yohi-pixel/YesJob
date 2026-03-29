from __future__ import annotations

from fastapi import APIRouter

from ai_agent.orchestrator.service import AIAgentService
from ai_agent.schemas.models import (
    HealthResponse,
    HRChatRequest,
    HRChatResponse,
    RecommendJobsRequest,
    RecommendJobsResponse,
    ResumeAdviceRequest,
    ResumeAdviceResponse,
)


router = APIRouter(prefix="/api/ai", tags=["ai-agent"])
service = AIAgentService()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        detail={
            "model": ("llm+rule-mvp-v1" if service.llm.enabled else "rule-mvp-v1"),
            "llm_enabled": service.llm.enabled,
        }
    )


@router.post("/recommend-jobs", response_model=RecommendJobsResponse)
def recommend_jobs(payload: RecommendJobsRequest) -> RecommendJobsResponse:
    return service.recommend_jobs(payload)


@router.post("/hr-chat", response_model=HRChatResponse)
def hr_chat(payload: HRChatRequest) -> HRChatResponse:
    return service.hr_chat(payload)


@router.post("/resume-advice", response_model=ResumeAdviceResponse)
def resume_advice(payload: ResumeAdviceRequest) -> ResumeAdviceResponse:
    return service.resume_advice(payload)
