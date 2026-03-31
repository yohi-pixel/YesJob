"""Extract structured experience items from a section of text."""

from __future__ import annotations

import re

from .schemas import ExperienceItem


# A single experience block starts with a title / org / role line
_BLOCK_RE = re.compile(r"(?:^|\n)(?=[^\n])", re.MULTILINE)

_DATE_RE = re.compile(
    r"(\d{4}[\./\-年]\s*\d{0,2}[\./\-月]?)\s*[-~—到至]\s*(\d{4}[\./\-年]\s*\d{0,2}[\./\-月]?|至今|现在|present|now)"
)


def extract_experiences(text: str) -> list[ExperienceItem]:
    """Best-effort extraction of ExperienceItem list from experience section text."""
    if not text.strip():
        return []

    items: list[ExperienceItem] = []

    # Split into blocks by consecutive blank lines or heading-like lines
    blocks = re.split(r"\n\s*\n", text.strip())

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split("\n")
        item = ExperienceItem()

        # Try to extract date range from first/second line
        date_match = _DATE_RE.search(block)
        if date_match:
            item.period = f"{date_match.group(1)} - {date_match.group(2)}"
            # Remove date line from further processing
            remaining = block[:date_match.start()] + block[date_match.end():]
        else:
            remaining = block

        # First non-empty line is usually title/org
        remaining_lines = [l.strip() for l in remaining.split("\n") if l.strip()]
        if remaining_lines:
            first = remaining_lines[0]
            # Common patterns: "项目名 - 角色" or "公司名 | 岗位"
            if " - " in first or "—" in first:
                sep = " - " if " - " in first else "—"
                parts = first.split(sep, 1)
                item.title = parts[0].strip()
                item.role = parts[1].strip()
            elif "|" in first or "｜" in first:
                sep = "|" if "|" in first else "｜"
                parts = first.split(sep, 1)
                item.organization = parts[0].strip()
                item.role = parts[1].strip()
            else:
                item.title = first
            remaining_lines = remaining_lines[1:]

        # Remaining lines → description + tech stack detection
        desc_lines = []
        tech_words: set[str] = set()
        _TECH_RE = re.compile(
            r"\b(?:Python|Java|C\+\+|JavaScript|TypeScript|Go|Rust|React|Vue|"
            r"Angular|Node\.?js|Spring|Django|Flask|FastAPI|Docker|Kubernetes|"
            r"MySQL|PostgreSQL|MongoDB|Redis|Git|Linux|AWS|Azure|TensorFlow|"
            r"PyTorch|pandas|numpy|scikit-learn|Hadoop|Spark|Kafka|RabbitMQ|"
            r"Webpack|Vite|Tailwind|CSS|HTML|SQL|NoSQL|REST|GraphQL|gRPC|"
            r"微服务|前后端|全栈|爬虫|数据分析|机器学习|深度学习)\b",
            re.IGNORECASE,
        )

        for line in remaining_lines:
            tech_found = _TECH_RE.findall(line)
            tech_words.update(t for t in tech_found)
            desc_lines.append(line)

        item.description = "\n".join(desc_lines)
        item.tech_stack = sorted(tech_words)

        if item.title or item.description:
            items.append(item)

    return items
