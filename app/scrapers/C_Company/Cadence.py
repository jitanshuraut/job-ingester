from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class CadenceScraper(BaseScraper):
    PAGE_SIZE = 20

    def _fetch_page(self, offset: int) -> dict:
        url = "https://cadence.wd1.myworkdayjobs.com/wday/cxs/cadence/External_Careers/jobs"
        payload = {
            "appliedFacets": {"locations": ["6418637d4d5010bf8a99bda155db6142", "d1bbeffd71a2100121c577c184b10000", "6418637d4d5010bf8a99b84a103c613d", "99daf6c35e5010011f3a4faaf3320000", "6418637d4d5010bf8a99b21035266138", "84b6cfd69db310b0db9d79bf33759a36", "6418637d4d5010bf8a99a4926e59612e", "6418637d4d5010bf8a99abd03be56133"], "timeType": ["59ec2ade908946248e84acbf58584a93"], "Location_Country": ["c4f78be1a8f14da0ab49ce1162348a5e"]},
            "limit": self.PAGE_SIZE,
            "offset": offset,
            "searchText": "",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Referer": "cadence.wd1.myworkdayjobs.com",
            "Origin": "cadence.wd1.myworkdayjobs.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        total = first.get("total", 0)
        all_items = list(first.get("jobPostings", []))
        for offset in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            data = self._fetch_page(offset)
            all_items.extend(data.get("jobPostings", []))
        return self._parse_items(all_items)

    def parse(self, data) -> list[Job]:
        return self._parse_items(data.get("jobPostings", []))

    def _parse_items(self, items: list) -> list[Job]:
        job_list = []
        for item in items:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("bulletFields")[0],
                company="Cadence",
                location=item.get("locationsText", ""),
                url=f"https://cadence.wd1.myworkdayjobs.com/en-US/External_Careers{item.get('externalPath', '')}" if item.get("externalPath") else "",
                posted_date=convert_to_common_format(item.get("postedOn", "")),
            )
            job_list.append(job)
        return job_list
