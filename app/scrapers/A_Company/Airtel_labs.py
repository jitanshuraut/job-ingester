from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from fake_useragent import UserAgent
from app.utils.DateConverter import convert_to_common_format

class AirtelLabsScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://airtel.darwinbox.in/ms/candidateapi/job?department=a66b91c788be2d&exp_from=1&page=1&limit=10"
        headers = {
            'User-Agent': UserAgent().random,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'https://airtel.darwinbox.in/ms/candidate/careers',
            'Origin': 'https://airtel.darwinbox.in/ms/candidate/careers',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        try:
            response = requests.get(
                url,headers=headers,timeout=30)
            json_data = response.json()
            print(response.status_code)
            return json_data
        except json.JSONDecodeError:
            print("Response is not valid JSON")
            print("Response text:")
            print(
                response.text[:500] + "..." if len(response.text) > 500 else response.text)
            return response.text

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        job_posts = data.get("message",{}).get("jobs",[])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("designation_display_name", ""),
                jobid=item.get("id"),
                company="AirtelLabs",
                location=item.get("officelocation_show_arr", ""),
                url=item.get("externalPath", ""),
                posted_date=convert_to_common_format(item.get("created_on", "")),
            )
            job_list.append(job)
        return job_list



