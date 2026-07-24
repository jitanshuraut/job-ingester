from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from urllib.parse import quote
from app.utils.DateConverter import convert_to_common_format


class DellScraper(BaseScraper):
    LIMIT = 200

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Content-Type': 'application/vnd.oracle.adf.resourceitem+json;charset=utf-8',
            'Referer': 'https://ehpv.fa.em2.oraclecloud.com/',
        })

    def _fetch_page(self, offset: int = 0) -> list[dict]:
        finder = (
            f"findReqs;siteNumber=CX_1,"
            f"facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,"
            f"limit={self.LIMIT},offset={offset},"
            f"locationId=300000000273955,selectedLocationsFacet=300000000273955,"
            f"sortBy=POSTING_DATES_DESC"
        )
        params = {
            "onlyData": "true",
            "expand": "requisitionList.workLocation",
            "finder": finder,
        }
        try:
            response = self._session.get(
                "https://ehpv.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions",
                params=params, timeout=30,
            )
            print(response.status_code)
            data = response.json()
            return data.get("items", [{}])[0].get("requisitionList", [])
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return []

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        all_reqs = list(self._fetch_page(0))
        if len(all_reqs) >= self.LIMIT:
            for offset in range(self.LIMIT, 2000, self.LIMIT):
                batch = self._fetch_page(offset)
                if not batch:
                    break
                all_reqs.extend(batch)
        return self._parse_reqs(all_reqs)

    def parse(self, data: list) -> list[Job]:
        return self._parse_reqs(data)

    TECH_KEYWORDS = [
        "software", "engineer", "developer", "architect",
        "data", "cloud", "devops", "sre", "platform",
        "infrastructure", "security", "full stack",
        "frontend", "backend", "technical", "product",
    ]

    def _is_tech_role(self, title: str) -> bool:
        t = title.lower()
        return any(f" {kw} " in f" {t} " or t.startswith(kw) or t.endswith(kw) for kw in self.TECH_KEYWORDS)

    def _parse_reqs(self, reqs: list) -> list[Job]:
        job_list = []
        for r0 in reqs:
            title = r0.get("Title", "")
            if not self._is_tech_role(title):
                continue
            wl = r0.get("workLocation", [{}])
            city = wl[0].get("City", "") if isinstance(wl, list) and wl else ""
            loc_parts = [city, r0.get("PrimaryLocation", "")]
            location = ", ".join(p for p in loc_parts if p)
            job_list.append(Job(
                title=title,
                jobid=str(r0.get("Id", "")),
                company="Dell",
                location=location,
                url="",
                posted_date=convert_to_common_format(r0.get("PostedDate", "")),
            ))
        return job_list
