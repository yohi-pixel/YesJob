"""Meituan campus jobs spider.

Flow: POST list (paginated) -> POST detail (per item) -> JobItem.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Any

import scrapy
from scrapy.http import JsonRequest

from crawlers.items import JobItem

COMPANY = "美团"
BASE_URL = "https://zhaopin.meituan.com"

API_LIST = f"{BASE_URL}/api/official/job/getJobList"
API_DETAIL = f"{BASE_URL}/api/official/job/getJobDetail"

_HEADERS = {
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/web/campus",
}


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    s = re.sub(r"\r\n?|\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip() or None


def _strip_html(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value)
    s = s.replace("<br/>", "\n").replace("<br />", "\n").replace("<br>", "\n")
    s = re.sub(r"</p>\s*<p>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)
    return _clean(s)


def _to_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, dict):
                text = _clean(
                    item.get("name")
                    or item.get("label")
                    or item.get("tagName")
                    or item.get("cityName")
                )
            else:
                text = _clean(item)
            if text:
                out.append(text)
        seen: set[str] = set()
        dedup: list[str] = []
        for t in out:
            if t not in seen:
                seen.add(t)
                dedup.append(t)
        return dedup
    if isinstance(value, str):
        parts = re.split(r"[|,，/\\]+", value)
        return [p.strip() for p in parts if p and p.strip()]
    return []


def _join_names(value: Any) -> str | None:
    names = _to_list(value)
    if not names:
        return None
    return " / ".join(names)


def _extract_data(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    return payload


class MeituanSpider(scrapy.Spider):
    name = "meituan"
    custom_settings = {
        "DOWNLOAD_DELAY": 0.4,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
    }

    def __init__(
        self,
        start_page: int = 1,
        end_page: int = 9999,
        page_size: int = 20,
        keywords: str = "",
        job_share_type: str = "1",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.start_page = int(start_page)
        self.end_page = int(end_page)
        self.page_size = int(page_size)
        self.keywords = keywords
        self.job_share_type = str(job_share_type)

    def start_requests(self):
        meta = {"page": self.start_page}
        yield self._list_request(self.start_page, meta)

    # -- Pagination ---------------------------------------------------------

    def _list_payload(self, page: int) -> dict[str, Any]:
        return {
            "page": {"pageNo": page, "pageSize": self.page_size},
            "keywords": self.keywords,
        }

    def _list_request(self, page: int, meta: dict[str, Any]):
        return JsonRequest(
            url=API_LIST,
            data=self._list_payload(page),
            headers=_HEADERS,
            callback=self.parse_list,
            meta=dict(meta, page=page),
        )

    def parse_list(self, response):
        payload = response.json()
        data = _extract_data(payload)
        meta = response.meta
        page = int(meta["page"])

        rows = data.get("list") or data.get("jobList") or []
        if not isinstance(rows, list):
            rows = []

        # Meituan list API does not provide stable total count in response.
        # Full update strategy: crawl page by page until list is empty
        # (or page-info indicates no next page), bounded by end_page.
        if not rows:
            self.logger.info(f"[meituan] stop at page={page}: empty list")
            return

        fetched_at = dt.datetime.now(dt.timezone.utc).isoformat()
        for row in rows:
            if not isinstance(row, dict):
                continue
            job_union_id = _clean(row.get("jobUnionId") or row.get("jobId") or row.get("id"))
            if not job_union_id:
                continue
            yield JsonRequest(
                url=API_DETAIL,
                data={"jobUnionId": job_union_id, "jobShareType": self.job_share_type},
                headers=_HEADERS,
                callback=self.parse_detail,
                meta={
                    "list_item": row,
                    "source_page": meta["page"],
                    "fetched_at": fetched_at,
                },
            )

        if page >= self.end_page:
            self.logger.info(f"[meituan] stop at page={page}: reached end_page={self.end_page}")
            return

        page_info = data.get("page") if isinstance(data.get("page"), dict) else {}
        has_next = page_info.get("hasNext")
        if has_next is False:
            self.logger.info(f"[meituan] stop at page={page}: page.hasNext=False")
            return

        if len(rows) < self.page_size:
            self.logger.info(
                f"[meituan] stop at page={page}: len(rows)={len(rows)} < page_size={self.page_size}"
            )
            return

        yield self._list_request(page + 1, meta)

    def parse_detail(self, response):
        m = response.meta
        list_item = m["list_item"]

        payload = response.json()
        detail = _extract_data(payload)

        job_id = _clean(
            list_item.get("jobUnionId")
            or detail.get("jobUnionId")
            or list_item.get("jobId")
            or detail.get("jobId")
        )

        work_cities = (
            _to_list(detail.get("cityList"))
            or _to_list(list_item.get("cityList"))
            or _to_list(detail.get("workCityList"))
            or _to_list(list_item.get("workCityList"))
            or _to_list(detail.get("workCity"))
            or _to_list(list_item.get("workCity"))
        )

        tags = (
            _to_list(detail.get("tag"))
            or _to_list(list_item.get("tag"))
            or _to_list(detail.get("highLight"))
            or _to_list(list_item.get("highLight"))
            or _to_list(list_item.get("tagList"))
            or _to_list(list_item.get("labelList"))
            or _to_list(detail.get("tagList"))
        )

        departments = detail.get("department") or list_item.get("department")
        department_names = _join_names(departments)

        team_intro = _clean(detail.get("departmentIntro")) or department_names

        responsibilities = _strip_html(
            detail.get("jobDuty")
            or list_item.get("jobDuty")
            or detail.get("responsibilities")
            or detail.get("jobResponsibilities")
            or detail.get("description")
            or list_item.get("desc")
        )

        requirements = _strip_html(
            detail.get("jobRequirement")
            or list_item.get("jobRequirement")
            or detail.get("requirements")
            or detail.get("jobRequirements")
            or detail.get("qualification")
        )

        yield JobItem(
            company=COMPANY,
            job_id=job_id,
            title=_clean(list_item.get("name") or detail.get("name") or list_item.get("jobName")),
            recruit_type=_clean(
                detail.get("projectName")
                or list_item.get("projectName")
                or list_item.get("hiringTypeName")
                or detail.get("hiringTypeName")
                or list_item.get("campusType")
            ),
            job_category=_clean(
                detail.get("jobFamilyGroup")
                or list_item.get("jobFamilyGroup")
                or detail.get("jobFamily")
                or list_item.get("jobFamily")
                or list_item.get("jfName")
                or detail.get("jfName")
                or list_item.get("jobCategory")
            ),
            job_function=_clean(
                department_names
                or list_item.get("bgName")
                or detail.get("bgName")
                or detail.get("department")
            ),
            work_city=work_cities[0] if work_cities else None,
            work_cities=work_cities,
            team_intro=team_intro,
            responsibilities=responsibilities,
            requirements=requirements,
            bonus_points=_strip_html(detail.get("bonusPoints") or detail.get("plus") or detail.get("bonus")),
            tags=tags,
            publish_time=_clean(
                detail.get("refreshTime")
                or list_item.get("refreshTime")
                or detail.get("firstPostTime")
                or list_item.get("firstPostTime")
                or list_item.get("publishTime")
                or detail.get("publishTime")
                or list_item.get("updateTime")
            ),
            detail_url=(
                f"{BASE_URL}/web/position/detail?jobUnionId={job_id}&highlightType=campus"
                if job_id
                else None
            ),
            fetched_at=m["fetched_at"],
            source_page=m["source_page"],
        )
