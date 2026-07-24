from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests
import json


class NexthinkScraper(BaseScraper):
    ALGOLIA_APP = "0Y8OPVVAE1"
    ALGOLIA_KEY = "5f17b4a23d3d2b929a52ab5f010d2242"
    HITS_PER_PAGE = 50

    def _fetch_page(self, page: int) -> dict:
        url = f"https://{self.ALGOLIA_APP.lower()}-dsn.algolia.net/1/indexes/careers/query"
        params = {
            "x-algolia-agent": "Algolia for JavaScript (4.26.0)",
            "x-algolia-api-key": self.ALGOLIA_KEY,
            "x-algolia-application-id": self.ALGOLIA_APP,
        }
        payload = {
            "params": f"hitsPerPage={self.HITS_PER_PAGE}&page={page}&facets=%5B%22location%22%5D&filters="
        }
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://nexthink.com",
            "Referer": "https://nexthink.com/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        }
        try:
            r = requests.post(url, params=params, json=payload, headers=headers, timeout=30)
            return r.json()
        except Exception:
            return {}

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        hits = first.get("hits", [])
        total = first.get("nbHits", 0)
        if not hits:
            return []
        all_hits = list(hits)
        total_pages = (total // self.HITS_PER_PAGE) + 1
        for page in range(1, total_pages):
            data = self._fetch_page(page)
            all_hits.extend(data.get("hits", []))

        jobs = []
        for hit in all_hits:
            country = ""
            for cf in hit.get("customFieldValues", []):
                if cf.get("fieldLabel") == "Country/Region":
                    country = cf.get("valueLabel", "")
            if country != "India":
                continue
            title = hit.get("vacancyName", "")
            if not title:
                continue
            ref = hit.get("refNumber", "")
            location = hit.get("location", "")
            url_name = hit.get("urlJobName", "")
            url = f"https://nexthink.com/careers/open-positions/{url_name}" if url_name else ""
            jobs.append(Job(
                title=title,
                jobid=ref,
                company="Nexthink",
                location=location,
                url=url,
                posted_date=convert_to_common_format(hit.get("releasedDate", 0) / 1000),
            ))
        return jobs
