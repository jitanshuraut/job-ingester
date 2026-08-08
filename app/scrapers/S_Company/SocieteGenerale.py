from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests
import math
import re


class SocieteGeneraleScraper(BaseScraper):
    SEARCH_URL = "https://careers.societegenerale.com/en/search"
    TOKEN_URL = "https://careers.societegenerale.com/sg-careers-offers/get-token"
    PROXY_URL = "https://careers.societegenerale.com/search-proxy.php"
    API_URL = "https://api.socgen.com/business-support/it-for-it-support/cognitive-service-knowledge/api/v1/search-profile"
    PAGE_SIZE = 100

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })

    def _get_csrf_token(self) -> str:
        r = self._session.get(self.SEARCH_URL, timeout=30)
        m = re.search(r'\"csrfToken\"\s*:\s*\"([^\"]+)\"', r.text)
        return m.group(1) if m else ""

    def _get_bearer_token(self, csrf: str) -> str:
        r = self._session.get(self.TOKEN_URL, headers={
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRF-Token": csrf,
        }, timeout=30)
        return r.json().get("token", "")

    def _fetch_page(self, token: str, offset: int) -> dict:
        payload = {
            "profile": "ces_profile_sgcareers",
            "query": {
                "advanced": [
                    {"type": "multi", "name": "sourcecsv1", "op": "eq", "values": ["IND"]},
                ],
                "skipCount": self.PAGE_SIZE,
                "skipFrom": offset,
                "sort": "sourcedatetime1.desc",
            },
            "lang": "en",
            "responseType": "SearchResult",
        }
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://careers.societegenerale.com",
            "referer": self.SEARCH_URL,
            "x-proxy-url": self.API_URL,
            "authorization-api": f"Bearer {token}",
        }
        r = self._session.post(self.PROXY_URL, json=payload, headers=headers, timeout=30)
        return r.json()

    @staticmethod
    def _extract_jobid(url: str) -> str:
        path = url.rstrip("/").split("/")[-1]
        for suffix in ["-en", "-fr"]:
            if path.endswith(suffix):
                path = path[: -len(suffix)]
                break
        return path.split("-")[-1]

    @staticmethod
    def _extract_location(geo: str) -> str:
        parts = geo.split(";")
        city = parts[5] if len(parts) > 5 else ""
        country = parts[1] if len(parts) > 1 else "India"
        if city:
            return f"{city}, {country}"
        return country

    def fetch_jobs(self) -> list[Job]:
        csrf = self._get_csrf_token()
        if not csrf:
            return []
        token = self._get_bearer_token(csrf)
        if not token:
            return []

        first = self._fetch_page(token, 0)
        total = first.get("TotalCount", 0)
        if not total:
            return []
        total_pages = math.ceil(total / self.PAGE_SIZE)
        jobs = []
        for page in range(total_pages):
            data = self._fetch_page(token, page * self.PAGE_SIZE) if page > 0 else first
            docs = data.get("Result", {}).get("Docs", [])
            for doc in docs:
                title = doc.get("resulttitle", "")
                url = doc.get("resulturl", "")
                if not title or not url:
                    continue
                geo = doc.get("geo", "")
                modified = doc.get("modified", "")
                jobs.append(Job(
                    title=title,
                    jobid=self._extract_jobid(url),
                    company="SocieteGenerale",
                    location=self._extract_location(geo),
                    url=url,
                    posted_date=convert_to_common_format(modified),
                ))
        return jobs
