from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format
class AckoScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://acko.sensehq.in/careers/api/postings"
        
        params = {
            'offset': 0,
            'limit': 10,
            'location': '', 
            'department': 'Technology - Engineering - Central - Dev (Backend/Frontend/Mobile)'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://www.acko.com',
            'Origin': 'https://www.acko.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',  
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        try:
                response = requests.get(url, headers=headers, params=params,timeout=30)
                json_data = response.json()
                print(response.status_code)
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
        job_posts = data.get("content", [])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("id"),
                company="Acko",
                location=item.get("location", ""),
                url=item.get("link", ""),
                posted_date=convert_to_common_format(datetime.utcfromtimestamp(item.get("updated_on", "") / 1000))
            )
            job_list.append(job)
        return job_list
    
 


