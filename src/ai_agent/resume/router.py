"""FastAPI router for resume parsing and AI optimization."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from .schemas import (
    OptimizeRequest,
    OptimizeResponse,
    ParseResumeResponse,
)
from .parser import extract_text
from .splitter import split_sections
from .extractor import extract_experiences
from .optimizer import optimize_section, parse_fallback_with_ai

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/resume", tags=["resume"])

# Lazy-loaded LLM client (avoids circular import)
_llm_call = None


def _get_llm_call():
    """Get the LLM call function from the AI agent's LLM client."""
    global _llm_call
    if _llm_call is not None:
        return _llm_call

    try:
        from ai_agent.orchestrator.service import AIAgentService
        service = AIAgentService()

        async def _call(prompt: str) -> str:
            result = service.llm.chat(
                system_prompt="You are a professional resume assistant.",
                user_prompt=prompt,
                temperature=0.2,
                max_tokens=900,
            )
            return result

        _llm_call = _call
        return _llm_call
    except Exception as e:
        logger.warning("LLM client not available: %s", e)
        return None


# ── Parse uploaded resume ───────────────────────────────

@router.post("/parse", response_model=ParseResumeResponse)
async def parse_resume(file: UploadFile = File(...)):
    """Upload a PDF/DOCX file and extract experiences + self-description."""
    suffix = (file.filename or "").lower()
    if suffix not in (".pdf", ".docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    try:
        text = await extract_text(file)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to extract text: {e}")

    if not text.strip():
        raise HTTPException(status_code=422, detail="No text could be extracted from the file")

    llm_fn = _get_llm_call()
    return await _parse_resume_text(text, llm_fn)


async def _parse_resume_text(text: str, llm_fn=None) -> ParseResumeResponse:
    """Parse resume text into experiences + self-description with robust fallbacks."""
    clean_text = text.strip()
    if not clean_text:
        return ParseResumeResponse(experiences=[], self_description={}, parse_method="regex", raw_sections={})

    # Step 1: regex-based section splitting
    sections = split_sections(clean_text)

    has_experience = bool(sections.get("experience", "").strip())
    has_self_desc = bool(sections.get("self_description", "").strip())
    no_heading_detected = (
        sections.get("experience", "").strip() == clean_text
        and not sections.get("self_description", "").strip()
        and not sections.get("basic_info", "").strip()
        and not sections.get("education", "").strip()
    )

    if (not has_experience and not has_self_desc) or no_heading_detected:
        # No regex matches → try AI splitting first
        if llm_fn:
            try:
                ai_result = await parse_fallback_with_ai(clean_text, llm_fn)
                normalized = _normalize_ai_parse_result(ai_result)
                if normalized["experiences"] or _has_self_desc_content(normalized["self_description"]):
                    return ParseResumeResponse(
                        experiences=normalized["experiences"],
                        self_description=normalized["self_description"],
                        parse_method="ai_fallback",
                        raw_sections=sections,
                    )
            except Exception:
                logger.exception("AI fallback parse failed")

        # Heuristic fallback: parse from full text to maximize stability.
        experience_items = extract_experiences(clean_text)
        self_description = _extract_self_description(clean_text)
        return ParseResumeResponse(
            experiences=experience_items,
            self_description=self_description,
            parse_method="regex",
            raw_sections=sections,
        )

    # Step 2: structured extraction from experience section
    experience_source = sections.get("experience", "").strip() or clean_text
    experience_items = extract_experiences(experience_source)

    # Step 3: self-description extraction (fallback to full text when section missing)
    self_desc_text = sections.get("self_description", "").strip() or clean_text
    self_description = _extract_self_description(self_desc_text)

    return ParseResumeResponse(
        experiences=experience_items,
        self_description=self_description,
        parse_method="regex",
        raw_sections=sections,
    )


def _normalize_ai_parse_result(result: dict[str, Any]) -> dict[str, Any]:
    """Normalize AI parse result shape and types for response safety."""
    experiences_raw = result.get("experiences") if isinstance(result, dict) else []
    experiences = experiences_raw if isinstance(experiences_raw, list) else []

    self_raw = result.get("self_description") if isinstance(result, dict) else {}
    if not isinstance(self_raw, dict):
        self_raw = {}

    self_description = {
        "self_evaluation": str(self_raw.get("self_evaluation", "") or "").strip(),
        "career_objective": str(self_raw.get("career_objective", "") or "").strip(),
        "personal_summary": str(self_raw.get("personal_summary", "") or "").strip(),
        "tags": self_raw.get("tags") if isinstance(self_raw.get("tags"), list) else [],
    }

    return {
        "experiences": experiences,
        "self_description": self_description,
    }


def _has_self_desc_content(self_description: dict[str, Any]) -> bool:
    return bool(
        str(self_description.get("self_evaluation", "")).strip()
        or str(self_description.get("career_objective", "")).strip()
        or str(self_description.get("personal_summary", "")).strip()
    )


def _extract_self_description(text: str) -> dict:
    """Heuristic extraction of self_evaluation / career_objective / personal_summary."""
    if not text:
        return {"self_evaluation": "", "career_objective": "", "personal_summary": "", "tags": []}

    # If text is short, just dump it into self_evaluation
    if len(text) < 100:
        return {"self_evaluation": text, "career_objective": "", "personal_summary": "", "tags": []}

    # Try to find sub-sections
    result = {"self_evaluation": "", "career_objective": "", "personal_summary": "", "tags": []}

    import re

    objective_match = re.search(
        r"(?:求职意向|职业目标|Career\s*Objective)[:：]?\s*(.+?)(?:\n|$)",
        text,
        re.IGNORECASE,
    )
    if objective_match:
        result["career_objective"] = objective_match.group(1).strip()

    summary_match = re.search(
        r"(?:个人总结|Personal\s*Summary)[:：]?\s*(.+?)(?:\n|$)",
        text,
        re.IGNORECASE,
    )
    if summary_match:
        result["personal_summary"] = summary_match.group(1).strip()

    # Remaining text goes to self_evaluation
    remaining = text
    if result["career_objective"]:
        remaining = remaining.replace(result["career_objective"], "", 1)
    if result["personal_summary"]:
        remaining = remaining.replace(result["personal_summary"], "", 1)

    result["self_evaluation"] = remaining.strip()
    return result


# ── AI optimize a section ───────────────────────────────

@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_content(payload: OptimizeRequest):
    """Use DeepSeek to rewrite a resume section for a target job tag."""
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="Content is required")

    llm_fn = _get_llm_call()
    if llm_fn is None:
        raise HTTPException(status_code=503, detail="AI service is not available")

    result = await optimize_section(payload, llm_fn)
    return result
