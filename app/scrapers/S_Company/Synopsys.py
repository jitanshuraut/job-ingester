from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
from bs4 import BeautifulSoup
from app.utils.DateConverter import convert_to_common_format


class SynopsysScraper(BaseScraper):
    BASE_URL = "https://careers.synopsys.com/search-jobs/India/44408/2/1269750/22/79/50/2"

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })

    def fetch_raw(self):
        try:
            response = self._session.get(self.BASE_URL, timeout=30)
            print(response.status_code)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            print(f"Request failed")
            return ""

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, html: str) -> list[Job]:
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        items = soup.select("li.search-results-list__list-item")
        job_list = []
        for item in items:
            link = item.select_one("a.sr-job-link")
            if not link:
                continue
            title_el = link.select_one("h2")
            title = title_el.get_text(strip=True) if title_el else ""
            href = link.get("href", "")
            location_el = link.select_one("span.job-location")
            location = location_el.get_text(strip=True) if location_el else ""
            date_el = link.select_one("span.job-date-posted")
            posted_date = date_el.get_text(strip=True).replace("Posted:", "").strip() if date_el else ""
            jobid = link.get("data-job-id", "")
            if not jobid:
                jobid = item.select_one("[data-job-id]")
                if jobid:
                    jobid = jobid.get("data-job-id", "")
            if not location:
                jobid_span = link.select_one("span.jobId")
                if jobid_span:
                    jobid = jobid_span.get_text(strip=True).replace("Job ID:", "").strip()
            full_url = f"https://careers.synopsys.com{href}" if href else ""
            job = Job(
                title=title,
                jobid=jobid,
                company="Synopsys",
                location=location,
                url=full_url,
                posted_date=convert_to_common_format(posted_date),
            )
            job_list.append(job)
        return job_list
