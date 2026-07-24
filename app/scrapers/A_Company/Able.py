from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from app.utils.DateConverter import convert_to_common_format

class AbleScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://job-boards.greenhouse.io/able"
        params = {
            'keyword': 'remote',
            '_data': 'routes/$url_token'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://job-boards.greenhouse.io/',
            'Origin': 'https://job-boards.greenhouse.io',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            print(response.status_code)
            return response.json()
        except (json.JSONDecodeError, requests.RequestException):
            print(f"Request failed")
            return {}

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        job_posts = data.get("jobPosts", {}).get("data", [])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("title", ""),
                jobid=str(item.get("id", "")),
                company="Able",
                location=item.get("location", ""),
                url=item.get("absolute_url", ""),
                posted_date=convert_to_common_format(item.get("updated_at", ""))
            )
            job_list.append(job)
        return job_list
