"""AI-powered optimization of resume sections using DeepSeek."""

from __future__ import annotations

import json
import logging
import re

from .schemas import OptimizeRequest, OptimizeResponse

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
你是一个专业的简历优化助手。用户会给你一段简历内容和一个目标岗位标签。
请根据目标岗位的要求，优化重写这段内容，使其更贴合该岗位的招聘需求。

要求：
1. 保持事实真实性，不编造经历
2. 使用 STAR 法则（情境-任务-行动-结果）优化项目描述
3. 突出与目标岗位相关的技能和成果
4. 语言简洁专业，使用动词开头
5. 适当加入量化指标（如果原文有相关数据）

请直接返回优化后的文本，不要加任何解释或前缀。"""

_EXPERIENCE_PROMPT = """\
请优化以下项目/实习经历描述，使其更贴合「{tag}」岗位的要求。

原文：
{content}

优化后的描述："""

_SELF_DESC_PROMPT = """\
请优化以下自我描述，使其更贴合「{tag}」岗位的要求。

原文：
{content}

优化后的描述："""


async def optimize_section(
    request: OptimizeRequest,
    llm_call,
) -> OptimizeResponse:
    """Call DeepSeek LLM to rewrite a resume section for a target job tag.

    Args:
        request: The optimization request with content, target_tag, section_type.
        llm_call: An async callable(text) -> str that invokes the LLM.
    """
    tag = request.target_tag or "通用"
    content = request.content.strip()

    if not content:
        return OptimizeResponse(
            optimized_content="",
            original_content="",
            target_tag=tag,
        )

    if request.section_type == "self_description":
        user_prompt = _SELF_DESC_PROMPT.format(tag=tag, content=content)
    else:
        user_prompt = _EXPERIENCE_PROMPT.format(tag=tag, content=content)

    try:
        full_prompt = f"{_SYSTEM_PROMPT}\n\n{user_prompt}"
        optimized = await llm_call(full_prompt)
        optimized = optimized.strip()
    except Exception:
        logger.exception("AI optimization failed, returning original content")
        optimized = content

    return OptimizeResponse(
        optimized_content=optimized,
        original_content=content,
        target_tag=tag,
    )


async def parse_fallback_with_ai(
    text: str,
    llm_call,
) -> dict:
    """Use AI to split raw text into experience and self-description sections.

    Returns {"experiences": [...], "self_description": {...}}.
    """
    prompt_template = """\
你是一个简历解析助手。请将以下简历文本拆分为两个部分，并以 JSON 格式返回。

JSON 格式要求：
{
  "experiences": [
    {
      "title": "项目名称",
      "role": "角色/职位",
      "organization": "公司/组织",
      "period": "时间段",
      "tech_stack": ["技术栈"],
      "description": "详细描述",
      "tags": []
    }
  ],
  "self_description": {
    "self_evaluation": "自我评价内容",
    "career_objective": "求职意向内容",
    "personal_summary": "个人总结内容",
    "tags": []
  }
}

简历文本：
__RESUME_TEXT__

请仅返回 JSON，不要加任何其他文字。"""

    try:
        prompt = prompt_template.replace("__RESUME_TEXT__", text[:3000])
        result = await llm_call(prompt)
        # Extract JSON from response (handle potential markdown wrapping)
        json_str = result.strip()
        if json_str.startswith("```"):
            json_str = re.sub(r"^```(?:json)?\n?", "", json_str)
            json_str = re.sub(r"\n?```$", "", json_str)
        return json.loads(json_str)
    except Exception:
        logger.exception("AI parse fallback failed")
        return {"experiences": [], "self_description": {}}
