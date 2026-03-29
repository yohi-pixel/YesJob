from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_job(job: dict[str, Any]) -> dict[str, Any]:
    work_cities = job.get("work_cities")
    if isinstance(work_cities, str):
        work_cities = [s.strip() for s in work_cities.split("|") if s.strip()]
    elif not isinstance(work_cities, list):
        work_cities = []

    search_blob = str(job.get("search_blob") or "").strip()
    if not search_blob:
        search_blob = " ".join(
            str(job.get(field, "") or "")
            for field in ["title", "responsibilities", "requirements", "bonus_points", "job_category", "job_function"]
        ).strip()

    normalized = dict(job)
    normalized["work_cities"] = work_cities
    normalized["search_blob"] = search_blob
    normalized["search_blob_lower"] = search_blob.lower()
    normalized["project"] = str(job.get("job_function") or job.get("recruit_type") or "").strip()
    return normalized


@lru_cache(maxsize=1)
def load_jobs(data_root: str = "web/data") -> list[dict[str, Any]]:
    root = Path(data_root)
    if not root.exists():
        return []

    index_path = root / "jobs.index.json"
    if index_path.exists():
        try:
            index_payload = _read_json(index_path)
            chunks = index_payload.get("chunks", [])
            all_jobs: list[dict[str, Any]] = []
            for chunk in chunks:
                name = chunk.get("file")
                if not name:
                    continue
                chunk_path = root / "chunks" / str(name)
                if not chunk_path.exists():
                    continue
                records = _read_json(chunk_path)
                if isinstance(records, list):
                    all_jobs.extend(_normalize_job(x) for x in records if isinstance(x, dict))
            if all_jobs:
                return all_jobs
        except Exception:
            pass

    jobs_path = root / "jobs.json"
    if jobs_path.exists():
        try:
            payload = _read_json(jobs_path)
            if isinstance(payload, list):
                return [_normalize_job(x) for x in payload if isinstance(x, dict)]
        except Exception:
            return []

    return []


def clear_jobs_cache() -> None:
    load_jobs.cache_clear()
