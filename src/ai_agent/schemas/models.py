from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    education: str = ""
    major: str = ""
    grade: str = ""
    skills: list[str] = Field(default_factory=list)
    experience_summary: str = ""
    city_preferences: list[str] = Field(default_factory=list)
    industry_preferences: list[str] = Field(default_factory=list)
    intent: str = ""


class RecommendConstraints(BaseModel):
    recruit_type: str = ""
    job_category: str = ""
    city: str = ""
    company_whitelist: list[str] = Field(default_factory=list)
    company_blacklist: list[str] = Field(default_factory=list)


class RecommendJobsRequest(BaseModel):
    session_id: str = ""
    user_profile: UserProfile = Field(default_factory=UserProfile)
    constraints: RecommendConstraints = Field(default_factory=RecommendConstraints)
    top_k: int = 8


class JobCard(BaseModel):
    company: str = ""
    job_id: str = ""
    title: str = ""
    recruit_type: str = ""
    job_category: str = ""
    job_function: str = ""
    work_city: str = ""
    publish_time: str = ""
    detail_url: str = ""
    match_score: float = 0.0
    match_reasons: list[str] = Field(default_factory=list)


class RecommendTrace(BaseModel):
    retrieved_count: int = 0
    filtered_count: int = 0
    model_version: str = "rule-mvp-v1"


class RecommendJobsResponse(BaseModel):
    answer: str
    jobs: list[JobCard]
    trace: RecommendTrace


class HRChatRequest(BaseModel):
    session_id: str
    message: str
    top_k: int = 8


class HRChatResponse(BaseModel):
    session_id: str
    phase: str = "clarifying"
    assistant_message: str
    follow_up_questions: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    collected_profile: UserProfile = Field(default_factory=UserProfile)
    collected_constraints: RecommendConstraints = Field(default_factory=RecommendConstraints)
    conversation_summary: str = ""
    llm_used: bool = False
    fallback_reason: str = ""
    recommend_result: RecommendJobsResponse | None = None


class ResumeAdviceRequest(BaseModel):
    session_id: str = ""
    user_profile: UserProfile = Field(default_factory=UserProfile)
    resume_text: str = ""
    target_jobs: list[JobCard] = Field(default_factory=list)
    target_job_ids: list[str] = Field(default_factory=list)


class ResumeDiagnosis(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)


class ResumeSuggestions(BaseModel):
    p0: list[str] = Field(default_factory=list)
    p1: list[str] = Field(default_factory=list)
    p2: list[str] = Field(default_factory=list)


class ResumeAdviceResponse(BaseModel):
    diagnosis: ResumeDiagnosis
    suggestions: ResumeSuggestions
    rewritten_bullets: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "ai-agent"
    detail: dict[str, Any] = Field(default_factory=dict)
