from __future__ import annotations

from typing import Any

from ai_agent.schemas.models import RecommendJobsRequest


def score_job(job: dict[str, Any], request: RecommendJobsRequest, query_tokens: list[str]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    profile = request.user_profile
    constraints = request.constraints
    blob = str(job.get("search_blob_lower") or "")

    if constraints.job_category and constraints.job_category in str(job.get("job_category") or ""):
        score += 20
        reasons.append(f"岗位类别命中：{constraints.job_category}")

    if constraints.recruit_type and constraints.recruit_type in str(job.get("recruit_type") or ""):
        score += 10
        reasons.append(f"招聘类型匹配：{constraints.recruit_type}")

    preferred_cities = set(profile.city_preferences)
    if constraints.city:
        preferred_cities.add(constraints.city)
    cities = set([str(job.get("work_city") or "").strip(), *[str(x).strip() for x in job.get("work_cities", [])]])
    city_hits = [city for city in preferred_cities if city and city in cities]
    if city_hits:
        score += 18
        reasons.append(f"城市偏好匹配：{'/'.join(city_hits[:2])}")

    skill_hits = [skill for skill in profile.skills if skill and skill.lower() in blob]
    if skill_hits:
        score += min(28, 6 * len(skill_hits))
        reasons.append(f"技能关键词命中：{'、'.join(skill_hits[:3])}")

    token_hits = [token for token in query_tokens if token.lower() in blob]
    if token_hits:
        score += min(24, 4 * len(token_hits))
        reasons.append(f"诉求关键词命中：{'、'.join(token_hits[:3])}")

    if profile.major and profile.major.lower() in blob:
        score += 8
        reasons.append(f"专业相关：{profile.major}")

    if not reasons:
        reasons.append("基础条件匹配，建议进一步查看岗位详情。")

    return round(score, 2), reasons[:4]


def rank_jobs(candidates: list[dict[str, Any]], request: RecommendJobsRequest, query_tokens: list[str]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for job in candidates:
        score, reasons = score_job(job, request, query_tokens)
        item = dict(job)
        item["match_score"] = score
        item["match_reasons"] = reasons
        ranked.append(item)

    ranked.sort(key=lambda x: (x.get("match_score", 0.0), str(x.get("publish_time", ""))), reverse=True)
    return ranked
