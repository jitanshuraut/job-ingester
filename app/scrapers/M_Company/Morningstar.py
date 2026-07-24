from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class MorningstarScraper(BaseScraper):
    PAGE_SIZE = 50

    def _build_payload(self, offset: int) -> dict:
        return {
            "lang": "en_us",
            "deviceType": "desktop",
            "country": "us",
            "pageName": "search-results",
            "ddoKey": "refineSearch",
            "sortBy": "",
            "subsearch": "",
            "from": offset,
            "jobs": True,
            "counts": False,
            "all_fields": ["country", "state", "city", "category"],
            "size": self.PAGE_SIZE,
            "pageType": "searchResults",
            "clearAll": False,
            "jdsource": "facets",
            "isSliderEnable": False,
            "siteType": "external",
            "keywords": "",
            "global": True,
            "selected_fields": {"country": ["India"]},
            "locationData": {},
            "rkstatus": True,
        }

    def _fetch_page(self, offset: int) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://careers.morningstar.com",
            "Referer": "https://careers.morningstar.com/us/en/c/product-development-jobs",
        }
        try:
            r = requests.post(
                "https://careers.morningstar.com/widgets",
                json=self._build_payload(offset),
                headers=headers,
                timeout=30,
            )
            return r.json()
        except (json.JSONDecodeError, requests.RequestException):
            return {}

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        rs = first.get("refineSearch", {})
        total = rs.get("totalHits", 0)
        all_items = list(rs.get("data", {}).get("jobs", []))
        for offset in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            data = self._fetch_page(offset)
            all_items.extend(
                data.get("refineSearch", {}).get("data", {}).get("jobs", [])
            )
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(
            data.get("refineSearch", {}).get("data", {}).get("jobs", [])
        )

    @staticmethod
    def _format_date(date_str: str) -> str:
        if not date_str:
            return ""
        return convert_to_common_format(date_str[:10])

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            job_list.append(Job(
                title=item.get("title", ""),
                jobid=item.get("jobId", ""),
                company="Morningstar",
                location=f"{item.get('city', '')}, {item.get('state', '')}",
                url=item.get("applyUrl", ""),
                posted_date=self._format_date(item.get("postedDate", "")),
            ))
        return job_list
