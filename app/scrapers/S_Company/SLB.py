from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class SLBScraper(BaseScraper):
    PAGE_SIZE = 20
    MAX_PAGES = 25

    def _fetch_page(self, offset: int) -> dict:
        url = "https://schlumbergerproduction0cs2zrh7.org.coveo.com/rest/search/v2?organizationId=schlumbergerproduction0cs2zrh7"
        payload = {
            "locale": "en",
            "debug": False,
            "tab": "default",
            "timezone": "Asia/Calcutta",
            "fieldsToInclude": ["title", "country", "city", "category", "date", "permanentid", "urihash"],
            "pipeline": "ATSJobsPipeline",
            "q": "",
            "cq": '@source==$"ATS_Jobs_Source - Prod"',
            "enableQuerySyntax": False,
            "searchHub": "CoveoJobsHub",
            "sortCriteria": "@title ascending",
            "numberOfResults": self.PAGE_SIZE,
            "firstResult": offset,
            "facets": [
                {
                    "field": "country",
                    "type": "specific",
                    "currentValues": [{"value": "India", "state": "selected"}],
                    "sortCriteria": "occurrences",
                    "numberOfValues": 8,
                }
            ],
            "facetOptions": {"freezeFacetOrder": False},
        }
        headers = {
            "Authorization": "Bearer xx914ae3d7-f62f-4dea-9368-2f78d68650e1",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Origin": "https://careers.slb.com",
            "Referer": "https://careers.slb.com/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print("Request failed")
            return {}

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        total = first.get("totalCount", 0)
        all_results = list(first.get("results", []))
        max_results = min(total, self.PAGE_SIZE * self.MAX_PAGES)
        for offset in range(self.PAGE_SIZE, max_results, self.PAGE_SIZE):
            data = self._fetch_page(offset)
            all_results.extend(data.get("results", []))
        return self._parse_items(all_results)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("results", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            raw = item.get("raw", item)
            location = ", ".join(filter(None, [
                raw.get("city", ""),
                ", ".join(raw.get("country", [])) if isinstance(raw.get("country"), list) else raw.get("country", "")
            ]))
            ts = raw.get("date", 0)
            if isinstance(ts, (int, float)):
                ts = ts / 1000 if ts > 1e11 else ts
            else:
                ts = 0
            job = Job(
                title=raw.get("title", ""),
                jobid=raw.get("urihash", ""),
                company="SLB",
                location=location,
                url=item.get("clickUri", ""),
                posted_date=convert_to_common_format(ts),
            )
            job_list.append(job)
        return job_list
