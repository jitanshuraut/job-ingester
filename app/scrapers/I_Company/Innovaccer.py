from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class InnovaccerScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://apply.workable.com/api/v3/accounts/innovaccer-analytics/jobs"

        payload = {"query":"","department":[449315,449316,449317,449318,449319,449326,449328,449329,449330,449331,449332,449333],"location":[{"country":"India","region":"Uttar Pradesh","city":"Noida","countryCode":"IN"}],"remote":[],"workplace":[],"worktype":[]}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'apply.workable.com',
            'Origin': 'apply.workable.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        try:
            response = requests.post(
                url, headers=headers,  json=payload, timeout=30)
            json_data = response.json()
            print(response.status_code)
            return json_data
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        job_posts = data.get("results",[])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("Id"),
                company="Innovaccer",
                location="Noida",
                url=item.get("externalPath", ""),
                posted_date=convert_to_common_format(item.get("published", "")),
            )
            job_list.append(job)
        return job_list
