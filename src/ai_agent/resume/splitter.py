"""Split raw resume text into sections."""

from __future__ import annotations

import re
from dataclasses import dataclass


# Section heading patterns (Chinese resume common headings)
_EXPERIENCE_PATTERNS = re.compile(
    r"(?:^|\n)\s*"
    r"(?:"
    r"项目经历|"
    r"项目经验|"
    r"实习经历|"
    r"实习经验|"
    r"工作经历|"
    r"工作经验|"
    r"实践经历|"
    r"实践经验|"
    r"[Pp]roject(?:\s*[Ee]xperience)?|"
    r"[Ii]nternship(?:\s*[Ee]xperience)?|"
    r"[Ww]ork(?:\s*[Ee]xperience)?"
    r")\s*(?:\n|$)",
)

_SELF_DESC_PATTERNS = re.compile(
    r"(?:^|\n)\s*"
    r"(?:"
    r"自我评价|"
    r"自我介绍|"
    r"求职意向|"
    r"个人总结|"
    r"个人简介|"
    r"职业目标|"
    r"[Ss]elf(?:\s*-?\s*[Ii]ntroduction)?|"
    r"[Cc]areer(?:\s+[Oo]bjective)?|"
    r"[Pp]ersonal(?:\s+[Ss]ummary)?"
    r")\s*(?:\n|$)",
)

_BASIC_INFO_PATTERNS = re.compile(
    r"(?:^|\n)\s*"
    r"(?:"
    r"基本信息|"
    r"基本资料|"
    r"个人信息|"
    r"个人资料|"
    r"[Bb]asic(?:\s+[Ii]nformation)?|"
    r"[Pp]ersonal(?:\s+[Ii]nformation)?"
    r")\s*(?:\n|$)",
)

_EDUCATION_PATTERNS = re.compile(
    r"(?:^|\n)\s*"
    r"(?:"
    r"教育经历|"
    r"教育背景|"
    r"学历|"
    r"[Ee]ducation(?:\s+[Bb]ackground)?|"
    r"[Aa]cademic(?:\s+[Bb]ackground)?"
    r")\s*(?:\n|$)",
)

# Any heading-like line (used to detect section boundaries)
_HEADING_RE = re.compile(r"^\s*.{2,30}?\s*$", re.MULTILINE)


def split_sections(text: str) -> dict[str, str]:
    """Return {"experience": ..., "self_description": ..., "basic_info": ..., "education": ...} from raw text.

    Falls back to returning everything under "experience" if no
    recognisable headings are found (AI fallback will then be used).
    """
    # Find all heading positions
    heading_positions: list[tuple[int, str]] = []

    for m in _BASIC_INFO_PATTERNS.finditer(text):
        heading_positions.append((m.start(), "basic_info"))
    for m in _EDUCATION_PATTERNS.finditer(text):
        heading_positions.append((m.start(), "education"))
    for m in _EXPERIENCE_PATTERNS.finditer(text):
        heading_positions.append((m.start(), "experience"))
    for m in _SELF_DESC_PATTERNS.finditer(text):
        heading_positions.append((m.start(), "self_description"))

    heading_positions.sort(key=lambda x: x[0])

    if not heading_positions:
        # No recognisable sections → return all as experience for AI fallback
        return {"experience": text, "self_description": "", "basic_info": "", "education": ""}

    sections: dict[str, str] = {
        "basic_info": "",
        "education": "",
        "experience": "",
        "self_description": ""
    }

    for i, (start, label) in enumerate(heading_positions):
        # Content starts after the heading line
        content_start = text.index("\n", start) if "\n" in text[start:] else len(text)
        content_start = min(content_start + 1, len(text))

        # Content ends at the next heading
        content_end = (
            heading_positions[i + 1][0] if i + 1 < len(heading_positions) else len(text)
        )

        chunk = text[content_start:content_end].strip()
        sections[label] = (sections[label] + "\n" + chunk).strip()

    return sections
