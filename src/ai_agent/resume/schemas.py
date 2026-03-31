"""Pydantic schemas for resume parsing and optimization."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Experience ──────────────────────────────────────────

class ExperienceItem(BaseModel):
    """A single project / internship / work entry."""
    title: str = ""
    role: str = ""
    organization: str = ""
    period: str = ""
    tech_stack: list[str] = Field(default_factory=list)
    description: str = ""
    tags: list[str] = Field(default_factory=list)  # job-position tags


# ── Self description ────────────────────────────────────

class SelfDescription(BaseModel):
    self_evaluation: str = ""
    career_objective: str = ""
    personal_summary: str = ""
    tags: list[str] = Field(default_factory=list)  # job-position tags


# ── Basic Info ─────────────────────────────────────────

class BasicInfo(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    school: str = ""
    degree: str = ""
    major: str = ""
    grade: str = ""


# ── Parse request / response ───────────────────────────

class ParseResumeRequest(BaseModel):
    """Client sends the raw text extracted from a PDF/DOCX."""
    text: str = ""


class ParseResumeResponse(BaseModel):
    experiences: list[ExperienceItem] = Field(default_factory=list)
    self_description: SelfDescription = Field(default_factory=SelfDescription)
    parse_method: str = ""  # "regex" | "ai_fallback"
    raw_sections: dict[str, str] = Field(default_factory=dict)


# ── AI optimize request / response ─────────────────────

class OptimizeRequest(BaseModel):
    content: str = ""
    target_tag: str = ""
    section_type: str = ""  # "experience" | "self_description"


class OptimizeResponse(BaseModel):
    optimized_content: str = ""
    original_content: str = ""
    target_tag: str = ""
