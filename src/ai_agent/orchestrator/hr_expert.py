from __future__ import annotations

import re

from ai_agent.schemas.models import RecommendConstraints, UserProfile
from ai_agent.utils.security import sanitize_string_list, sanitize_text
from ai_agent.utils.session_store import HRSessionState


CITY_ALIASES = {
    "北京": ["北京", "北京市", "beijing"],
    "上海": ["上海", "上海市", "shanghai"],
    "广州": ["广州", "广州市", "guangzhou"],
    "深圳": ["深圳", "深圳市", "shenzhen"],
    "杭州": ["杭州", "杭州市", "hangzhou"],
    "成都": ["成都", "成都市", "chengdu"],
    "南京": ["南京", "南京市", "nanjing"],
    "武汉": ["武汉", "武汉市", "wuhan"],
    "西安": ["西安", "西安市", "xian", "xi'an"],
    "重庆": ["重庆", "重庆市", "chongqing"],
    "苏州": ["苏州", "苏州市", "suzhou"],
}

KNOWN_CITIES = list(CITY_ALIASES.keys())

KNOWN_CATEGORIES = ["技术", "产品", "运营", "设计", "市场", "销售", "数据", "算法", "测试", "游戏"]

KNOWN_RECRUIT_TYPES = ["实习", "校招", "秋招", "春招", "社招"]

ROLE_KEYWORDS = [
    "后端",
    "backend",
    "前端",
    "frontend",
    "全栈",
    "fullstack",
    "算法",
    "algorithm",
    "数据分析",
    "data",
    "数据工程",
    "测试",
    "qa",
    "运维",
    "sre",
    "产品",
    "product",
    "运营",
    "operation",
    "设计",
    "design",
]


def _extract_skills(text: str) -> list[str]:
    candidates = re.findall(r"[A-Za-z][A-Za-z0-9+#.]{1,20}|[\u4e00-\u9fa5]{2,8}", text)
    blacklist = {"我们", "你们", "可以", "希望", "岗位", "工作", "方向", "负责", "要求"}
    skills = []
    for token in candidates:
        low = token.lower()
        if token in blacklist:
            continue
        if token in KNOWN_CITIES or token in KNOWN_CATEGORIES or token in KNOWN_RECRUIT_TYPES:
            continue
        if len(token) < 2:
            continue
        if low in {x.lower() for x in skills}:
            continue
        skills.append(token)
    return skills[:12]


def update_state_with_user_input(state: HRSessionState, message: str) -> None:
    text = sanitize_text(message, max_len=1200)
    if not text:
        return

    state.turns += 1
    state.history.append({"role": "user", "text": text})

    if len(text) > len(state.experience_summary):
        state.experience_summary = text

    lowered = text.lower()

    if not state.intent:
        if "想找" in text or "希望" in text or "意向" in text or "目标" in text or "求职" in text:
            state.intent = text[:120]
        else:
            matched_roles = [kw for kw in ROLE_KEYWORDS if kw in text or kw in lowered]
            if matched_roles:
                state.intent = " / ".join(matched_roles[:3])

    for canonical, aliases in CITY_ALIASES.items():
        if any(alias in text or alias in lowered for alias in aliases):
            if canonical not in state.city_preferences:
                state.city_preferences.append(canonical)

    for recruit_type in KNOWN_RECRUIT_TYPES:
        if recruit_type in text:
            state.recruit_type = recruit_type
    if not state.recruit_type:
        if "intern" in lowered:
            state.recruit_type = "实习"
        elif "campus" in lowered:
            state.recruit_type = "校招"

    for category in KNOWN_CATEGORIES:
        if category in text and not state.job_category:
            state.job_category = category
    if not state.job_category:
        if any(
            token in text or token in lowered
            for token in ["后端", "前端", "开发", "算法", "数据", "sre", "测试", "backend", "frontend", "data", "qa"]
        ):
            state.job_category = "技术"
        elif any(token in text or token in lowered for token in ["产品", "运营", "市场", "销售", "设计", "product", "operation", "design"]):
            state.job_category = "产品"

    if not state.city and state.city_preferences:
        state.city = state.city_preferences[0]

    if not state.major:
        major_match = re.search(r"([\u4e00-\u9fa5]{2,8}(工程|科学|技术|学|专业))", text)
        if major_match:
            state.major = major_match.group(1)

    if not state.grade:
        grade_match = re.search(r"(大一|大二|大三|大四|研一|研二|研三|应届)", text)
        if grade_match:
            state.grade = grade_match.group(1)

    extracted_skills = _extract_skills(text)
    merged_skills = list(dict.fromkeys(state.skills + extracted_skills))
    state.skills = merged_skills[:12]


def build_profile_from_state(state: HRSessionState) -> UserProfile:
    return UserProfile(
        education="",
        major=state.major,
        grade=state.grade,
        skills=sanitize_string_list(state.skills, item_max_len=40, max_items=12),
        experience_summary=sanitize_text(state.experience_summary, max_len=280),
        city_preferences=sanitize_string_list(state.city_preferences, item_max_len=20, max_items=8),
        industry_preferences=sanitize_string_list(state.industry_preferences, item_max_len=20, max_items=8),
        intent=sanitize_text(state.intent, max_len=140),
    )


def build_constraints_from_state(state: HRSessionState) -> RecommendConstraints:
    return RecommendConstraints(
        recruit_type=sanitize_text(state.recruit_type, max_len=20),
        job_category=sanitize_text(state.job_category, max_len=20),
        city=sanitize_text(state.city, max_len=20),
        company_whitelist=[],
        company_blacklist=[],
    )


def compute_missing_fields(state: HRSessionState) -> list[str]:
    missing: list[str] = []
    if not state.intent:
        missing.append("岗位方向")
    if not state.city_preferences:
        missing.append("意向城市")
    if not state.skills:
        missing.append("核心技能")
    if not state.recruit_type:
        missing.append("招聘类型(实习/校招)")
    if not state.job_category:
        missing.append("岗位类别")
    return missing


def build_follow_up_questions(state: HRSessionState, missing_fields: list[str]) -> list[str]:
    questions: list[str] = []
    if "岗位方向" in missing_fields:
        questions.append("你目标岗位更偏后端、算法、数据、产品还是运营？")
    if "意向城市" in missing_fields:
        questions.append("你优先考虑哪些城市？可以给 1-3 个。")
    if "核心技能" in missing_fields:
        questions.append("你最有把握的 3-5 个技能是什么？例如 Python、Java、SQL、机器学习。")
    if "招聘类型(实习/校招)" in missing_fields:
        questions.append("你当前是找实习、校招，还是都可以？")
    if "岗位类别" in missing_fields:
        questions.append("你偏好的岗位类别是什么？比如技术、产品、运营、设计。")

    if not questions:
        questions.append("为了进一步精准推荐，你对公司规模或行业方向有偏好吗？")

    return questions[:3]


def is_ready_for_recommendation(state: HRSessionState, missing_fields: list[str]) -> bool:
    if state.turns < 2:
        return False
    # Allow one optional missing field after enough turns.
    return len(missing_fields) <= 1
