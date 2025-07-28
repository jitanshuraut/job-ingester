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
                json_data = response.json()
                return json_data
        except json.JSONDecodeError:
                print("Response is not valid JSON")
                print("Response text:")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                return response.text

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        job_posts = data.get("jobPosts", {}).get("data", [])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("internal_job_id"),
                company="Able",
                location=item.get("location", ""),
                url=item.get("absolute_url", ""),
                posted_date=convert_to_common_format(item.get("published_at", ""))
            )
            job_list.append(job)
        return job_list
    
 

