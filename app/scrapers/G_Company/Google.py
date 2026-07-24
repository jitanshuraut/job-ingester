from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
import re
import json


class GoogleScraper(BaseScraper):
    BASE_URL = "https://www.google.com/about/careers/applications/jobs/results/"

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })

    def fetch_raw(self):
        try:
            r = self._session.get(self.BASE_URL, params={
                'q': 'Software Engineer',
                'location': 'India',
                'hl': 'en',
            }, timeout=30)
            print(r.status_code)
            r.raise_for_status()
            return r.text
        except requests.RequestException:
            return ""

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, html: str) -> list[Job]:
        if not html:
            return []
        blocks = re.findall(r'AF_initDataCallback\(\{(.*?)\}\);</script>', html, re.DOTALL)
        if len(blocks) < 2:
            return []
        data_match = re.search(r'data\s*:\s*(\[)', blocks[1], re.DOTALL)
        if not data_match:
            return []
        content = blocks[1][data_match.start(1):]
        depth = 0
        end = 0
        for k, ch in enumerate(content):
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    end = k + 1
                    break
        if end == 0:
            return []
        try:
            data = json.loads(content[:end])
        except json.JSONDecodeError:
            return []
        if not data or not isinstance(data[0], list):
            return []
        jobs = []
        for entry in data[0]:
            if len(entry) < 10:
                continue
            job_id = str(entry[0]) if entry[0] else ""
            title = str(entry[1]) if entry[1] else ""
            url = str(entry[2]) if entry[2] else ""
            company = str(entry[7]) if len(entry) > 7 and entry[7] else "Google"
            location = ""
            if len(entry) > 9 and isinstance(entry[9], list) and entry[9]:
                loc_data = entry[9][0]
                if isinstance(loc_data, list) and loc_data:
                    location = str(loc_data[0]) if loc_data[0] else ""
                elif isinstance(loc_data, str):
                    location = loc_data
            jobs.append(Job(
                title=title,
                jobid=job_id,
                company=company,
                location=location,
                url=url,
                posted_date="",
            ))
        return jobs
