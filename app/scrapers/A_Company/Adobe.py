from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.analyzer.extractor import analyze_job_description
from app.analyzer.fetcher import fetch_description_text
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class AdobeScraper(BaseScraper):
    PAGE_SIZE = 10

    def _fetch_page(self, from_val: int) -> dict:
        url = "https://careers.adobe.com/widgets"
        payload = {
            "lang": "en_us",
            "deviceType": "desktop",
            "country": "us",
            "pageName": "search-results",
            "ddoKey": "refineSearch",
            "sortBy": "",
            "subsearch": "",
            "from": from_val,
            "irs": False,
            "jobs": True,
            "counts": True,
            "all_fields": ["remote", "country", "state", "city", "experienceLevel", "category", "profession", "employmentType", "jobLevel"],
            "size": self.PAGE_SIZE,
            "clearAll": False,
            "jdsource": "facets",
            "isSliderEnable": False,
            "pageId": "page15-ds",
            "siteType": "external",
            "keywords": "",
            "global": True,
            "selected_fields": {"country": ["India"], "category": ["Engineering and Product"]},
            "locationData": {},
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Content-Type': 'application/json',
            'Referer': 'https://careers.adobe.com/us/en/search-results',
            'Origin': 'https://careers.adobe.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        all_items = list(first.get("refineSearch", {}).get("data", {}).get("jobs", []))
        total = 0
        for agg in first.get("refineSearch", {}).get("data", {}).get("aggregations", []):
            if agg.get("field") == "category":
                total = (agg.get("value") or {}).get("Engineering and Product", 0)
                break
        for from_val in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            data = self._fetch_page(from_val)
            all_items.extend(data.get("refineSearch", {}).get("data", {}).get("jobs", []))
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("refineSearch", {}).get("data", {}).get("jobs", []))

    @staticmethod
    def _job_url(apply_url: str) -> str:
        return apply_url.rstrip("/").removesuffix("/apply")

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            url = self._job_url(item.get("applyUrl", ""))
            description = fetch_description_text(url)
            analysis = analyze_job_description(description)
            payload_skills = item.get("ml_skills") or []
            skills = list(dict.fromkeys(list(payload_skills) + analysis["skills"]))
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("jobId"),
                company="Adobe",
                location=item.get("location", ""),
                url=url,
                posted_date=convert_to_common_format(item.get("postedDate", "")),
                experience_years=json.dumps(analysis["experience_years"]),
                skills=json.dumps(skills),
            )
            job_list.append(job)
        return job_list
