from __future__ import annotations

import re

from ai_agent.schemas.models import ResumeAdviceRequest, ResumeAdviceResponse, ResumeDiagnosis, ResumeSuggestions


KEYWORD_PATTERN = re.compile(r"[A-Za-z0-9\u4e00-\u9fa5+#.]{2,}")


def _extract_keywords(text: str, limit: int = 40) -> list[str]:
    seen: set[str] = set()
    tokens: list[str] = []
    for token in KEYWORD_PATTERN.findall(text or ""):
        key = token.lower()
        if key in seen:
            continue
        seen.add(key)
        tokens.append(token)
        if len(tokens) >= limit:
            break
    return tokens


def build_resume_advice(request: ResumeAdviceRequest) -> ResumeAdviceResponse:
    resume_text = request.resume_text or ""
    resume_lower = resume_text.lower()

    jd_text = "\n".join(
        " ".join(
            [
                str(job.title or ""),
                str(job.job_category or ""),
                str(job.job_function or ""),
                str(job.match_reasons or ""),
            ]
        )
        for job in request.target_jobs
    )

    jd_keywords = _extract_keywords(jd_text, limit=30)
    missing_keywords = [kw for kw in jd_keywords if kw.lower() not in resume_lower][:10]

    strengths: list[str] = []
    for skill in request.user_profile.skills:
        if skill and skill.lower() in resume_lower:
            strengths.append(f"简历中已体现核心技能：{skill}")
    if not strengths:
        strengths.append("具备基础背景信息，建议补充更量化的项目成果。")

    gaps: list[str] = []
    if missing_keywords:
        gaps.append("与目标岗位相比，部分关键能力词尚未在简历中明确体现。")
    if len(resume_text.strip()) < 120:
        gaps.append("简历文本较短，建议补充 1-2 段可量化项目经历。")
    if not gaps:
        gaps.append("核心能力覆盖较好，可进一步优化表达和数据化成果。")

    suggestions = ResumeSuggestions(
        p0=[
            "针对目标岗位，将最相关项目放在前两段，并补充结果指标（如性能提升、转化率、效率提升）。",
            "每段经历使用 STAR 结构：背景-动作-结果，避免只写职责不写产出。",
        ],
        p1=[
            "在技能区补齐岗位高频关键词，并确保与项目经历中的实践一一对应。",
            "对与目标岗位强相关的课程/竞赛/实习经历增加 1 条可验证成果。",
        ],
        p2=[
            "统一动词时态与格式，减少重复表述，提升 ATS 可读性。",
        ],
    )

    bullets = [
        "负责XX模块设计与实现，通过A/B方案优化使关键指标提升 20%+。",
        "主导跨团队协作推进XX项目，建立自动化流程将交付周期缩短 30%。",
        "围绕目标岗位关键词重构项目描述，突出问题难度、方案取舍与业务结果。",
    ]

    follow_up = [
        "你目标的岗位更偏后端、算法还是数据分析？",
        "是否有可以量化的项目成果（性能、成本、效率、转化）可补充？",
    ]

    return ResumeAdviceResponse(
        diagnosis=ResumeDiagnosis(
            strengths=strengths[:5],
            gaps=gaps[:5],
            missing_keywords=missing_keywords,
        ),
        suggestions=suggestions,
        rewritten_bullets=bullets,
        follow_up_questions=follow_up,
    )
