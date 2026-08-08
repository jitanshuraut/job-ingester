from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.analyzer.extractor import analyze_job_description
from app.analyzer.fetcher import fetch_description_text
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class AllianzScraper(BaseScraper):
    PAGE_SIZE = 10

    def _build_payload(self, offset: int) -> dict:
        return {
            "sortBy": "",
            "subsearch": "",
            "from": offset,
            "jobs": True,
            "counts": True,
            "all_fields": ["phLocSlider", "category", "country", "state", "city", "remote", "employmentType", "jobLevel", "type", "unit"],
            "pageName": "search-results",
            "size": self.PAGE_SIZE,
            "clearAll": False,
            "jdsource": "facets",
            "isSliderEnable": True,
            "pageId": "page3",
            "siteType": "external",
            "keywords": "",
            "global": True,
            "selected_fields": {"category": ["IT & Tech Engineering", "Data & AI"], "unit": ["Allianz Technology"]},
            "locationData": {
                "place_id": "ChIJkbeSa_BfYzARphNChaFPjNc",
                "sliderRadius": 50,
                "aboveMaxRadius": False,
                "LocationUnit": "miles",
                "placeVal": "India",
            },
            "s": "1",
            "lang": "en_global",
            "deviceType": "desktop",
            "country": "global",
            "refNum": "AISAIPGB",
            "ddoKey": "eagerLoadRefineSearch",
        }

    def _headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
            "Origin": "https://careers.allianz.com",
            "Referer": "https://careers.allianz.com/global/en/search-results?p=ChIJkbeSa_BfYzARphNChaFPjNc&location=India",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

    def _fetch_page(self, offset: int) -> dict:
        try:
            r = requests.post(
                "https://careers.allianz.com/widgets",
                json=self._build_payload(offset),
                headers=self._headers(),
                timeout=30,
            )
            print(r.status_code)
            return r.json()
        except (json.JSONDecodeError, requests.RequestException):
            print("Request failed")
            return {}

    @staticmethod
    def _results(data: dict) -> dict:
        return data.get("eagerLoadRefineSearch") or data.get("refineSearch") or {}

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        rs = self._results(first)
        all_jobs = list(rs.get("data", {}).get("jobs", []))
        total = rs.get("totalHits", len(all_jobs))
        for offset in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            page = self._fetch_page(offset)
            all_jobs.extend(self._results(page).get("data", {}).get("jobs", []))
        return self._parse_items(all_jobs)

    def parse(self, data: dict) -> list[Job]:
        return self._parse_items(self._results(data).get("data", {}).get("jobs", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for j in items:
            job_id = str(j.get("jobId") or j.get("reqId") or "")
            city = j.get("city", "") or ""
            state = j.get("state", "") or ""
            location = f"{city}, {state}".strip(", ")
            url = f"https://careers.allianz.com/global/en/job/{job_id}"
            description = fetch_description_text(url)
            analysis = analyze_job_description(description)
            payload_skills = j.get("ml_skills") or []
            skills = list(dict.fromkeys(list(payload_skills) + analysis["skills"]))
            job = Job(
                title=j.get("title", ""),
                jobid=job_id,
                company="Allianz",
                location=location if location else "India",
                url=url,
                posted_date=convert_to_common_format(j.get("postedDate", "")),
                experience_years=json.dumps(analysis["experience_years"]),
                skills=json.dumps(skills),
            )
            job_list.append(job)
        return job_list
