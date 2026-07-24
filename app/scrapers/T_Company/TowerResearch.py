from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import json
from datetime import datetime
from app.utils.DateConverter import convert_to_common_format


class TowerResearchScraper(BaseScraper):
    def fetch_raw(self):
        url = "https://job-boards.greenhouse.io/embed/job_board?for=towerresearchcapital&validityToken=dMTu-u_Z7bgcKmo3qZAdHEn4TNs2DZHn9Klgq7MmrXVrRUL0QfenjrkFq3_nTkW_NcbCC6KdB_Ok2_2ycxzUaZJRX-3gC_FkPTfdPFn2W7v2qwgRbNdINen5KHWbdDkhohNFcq5GC_Wq8C1FhiMBPkLLdcbh8BR3REPKdYi951Qp2SXIbFCbNwbXxJwU1LzvDLzhJnBX_-2SlMXbm08QGOGiWqXRz2ntjNr6vgmNkRtUwep4DZz2BeiyT35_i7x4QWcyUzni3kP09WfydwOZQta9yJWLZvqH6j8K7UCxATs3a7QsEvuGNRNY22fC7Q8oWD_Yl9UAxVDrvxGxUwg3HQ%3D%3D&offices%5B%5D=75204&offices%5B%5D=1295&offices%5B%5D=211960&departments%5B%5D=151826&departments%5B%5D=2129&departments%5B%5D=145345&departments%5B%5D=151551&_data=routes%2Fembed.job_board"

        

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Referer': 'job-boards.greenhouse.io',
            'Origin': 'job-boards.greenhouse.io',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        try:
            response = requests.get(
                url, headers=headers, timeout=30)
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
        job_posts = data.get("jobPosts",{}).get("data",[])
        job_list = []
        for item in job_posts:
            job = Job(
                title=item.get("title", ""),
                jobid=item.get("internal_job_id"),
                company="Tower Research",
                location=item.get("location", ""),
                url=item.get("absolute_url", ""),
                posted_date=convert_to_common_format(item.get("updated_at", "")),
            )
            job_list.append(job)
        return job_list
