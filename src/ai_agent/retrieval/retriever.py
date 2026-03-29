from __future__ import annotations

import re
from typing import Any

from ai_agent.schemas.models import RecommendJobsRequest


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9\u4e00-\u9fa5]{2,}")


def _tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text or "")


def build_query_tokens(request: RecommendJobsRequest) -> list[str]:
    profile = request.user_profile
    text_parts = [
        profile.major,
        profile.intent,
        profile.experience_summary,
        " ".join(profile.skills),
        " ".join(profile.industry_preferences),
        request.constraints.job_category,
    ]
    tokens: list[str] = []
    seen: set[str] = set()
    for part in text_parts:
        for token in _tokenize(part):
            low = token.lower()
            if low in seen:
                continue
            seen.add(low)
            tokens.append(token)
    return tokens


def _passes_constraints(job: dict[str, Any], request: RecommendJobsRequest) -> bool:
    constraints = request.constraints
    company = str(job.get("company") or "").strip()

    if constraints.company_whitelist and company not in constraints.company_whitelist:
        return False
    if constraints.company_blacklist and company in constraints.company_blacklist:
        return False

    if constraints.recruit_type:
        if constraints.recruit_type not in str(job.get("recruit_type") or ""):
            return False

    if constraints.job_category:
        if constraints.job_category not in str(job.get("job_category") or ""):
            return False

    selected_city = constraints.city.strip()
    if selected_city:
        cities = set([str(job.get("work_city") or "").strip(), *[str(x).strip() for x in job.get("work_cities", [])]])
        if selected_city not in cities:
            return False

    return True


def retrieve_candidates(jobs: list[dict[str, Any]], request: RecommendJobsRequest, limit: int = 200) -> tuple[list[dict[str, Any]], list[str]]:
    tokens = build_query_tokens(request)

    constrained = [job for job in jobs if _passes_constraints(job, request)]
    if not tokens:
        return constrained[:limit], tokens

    scored: list[tuple[int, dict[str, Any]]] = []
    for job in constrained:
        blob = str(job.get("search_blob_lower") or "")
        hit = sum(1 for token in tokens if token.lower() in blob)
        if hit:
            scored.append((hit, job))

    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return constrained[:limit], tokens
    return [job for _, job in scored[:limit]], tokens
