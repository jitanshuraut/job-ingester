from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class AmdocsScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://jobs.amdocs.com/api/apply/v2/jobs?domain=amdocs.com&profile=&location=any&seniority=Entry&pid=563431003690524&job%20location=india-%20pune%20%28amdocs%20site%29&job%20location=india-%20gurgaon%20%28amdocs%20site%29&domain=amdocs.com&sort_by=relevance"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'jobs.amdocs.com',
            'Origin': 'jobs.amdocs.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        try:
            response = requests.get(
                url,headers=headers,timeout=30)
            print(response.status_code)
            json_data = response.json()
            return json_data
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        items = data.get("positions", [])
        job_list = []
        for item in items:
            job = Job(
                title=item.get("name", ""),
                jobid=item.get("display_job_id"),
                company="Amdocs",
                location=item.get("location", ""),
                url=item.get("apply_url", ""),
                posted_date=convert_to_common_format(item.get("t_update", "")),
            )
            job_list.append(job)
        return job_list


if __name__ == "__main__":
    listener = AmdocsScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)
