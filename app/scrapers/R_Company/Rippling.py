from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format


class RipplingScraper(BaseScraper):
    PAGE_SIZE = 50

    def _fetch_page(self, page: int) -> dict:
        url = "https://6fnax3tbef-dsn.algolia.net/1/indexes/*/queries"
        params = {
            "x-algolia-agent": "Algolia for JavaScript (5.23.4); Lite (5.23.4); Browser; instantsearch.js (4.78.1); react (18.3.1); react-instantsearch (7.15.5); next.js (14.2.35); JS Helper (3.24.3)",
            "x-algolia-api-key": "416caa4690f002ff6fe4a2097623640b",
            "x-algolia-application-id": "6FNAX3TBEF",
        }
        payload = {
            "requests": [
                {
                    "indexName": "careers_en-US_production",
                    "clickAnalytics": False,
                    "facetFilters": [
                        ["departmentName:Engineering"],
                        ["locationNames:Bangalore, India", "locationNames:Remote"],
                    ],
                    "hitsPerPage": self.PAGE_SIZE,
                    "query": "",
                    "page": page,
                },
            ],
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'https://www.rippling.com',
            'Referer': 'https://www.rippling.com/',
        }
        response = requests.post(url, json=payload, params=params, headers=headers, timeout=30)
        print(response.status_code)
        return response.json()

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        res = (first.get("results") or [{}])[0]
        nb_pages = res.get("nbPages", 1)
        all_hits = list(res.get("hits", []))
        for page in range(1, nb_pages):
            try:
                data = self._fetch_page(page)
                hits = ((data.get("results") or [{}])[0]).get("hits", [])
                all_hits.extend(hits)
            except (json.JSONDecodeError, requests.RequestException):
                print(f"Failed to fetch page {page}")
        return self._parse_hits(all_hits)

    def parse(self, data) -> list[Job]:
        results = data.get("results", [])
        hits = results[0].get("hits", []) if results else []
        return self._parse_hits(hits)

    def _parse_hits(self, hits: list) -> list[Job]:
        job_list = []
        for item in hits:
            job = Job(
                title=item.get("name", ""),
                jobid=item.get("jobId", ""),
                company="Rippling",
                location=", ".join(item.get("locationNames", [])),
                url=item.get("url", ""),
                posted_date=None,
            )
            job_list.append(job)
        return job_list
