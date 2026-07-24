from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
from bs4 import BeautifulSoup


class CitiScraper(BaseScraper):
    BASE_URL = "https://jobs.citi.com/search-jobs/software/India/287/1/2/1269750/22/79/50/2"

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })

    def fetch_raw(self):
        try:
            r = self._session.get(self.BASE_URL, timeout=30)
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
        soup = BeautifulSoup(html, "lxml")
        items = soup.select("li.sr-job-item")
        jobs = []
        for item in items:
            link = item.select_one("a[href*=\"/job/\"]")
            title = link.get_text(strip=True) if link else ""
            href = link.get("href", "") if link else ""
            btn = item.select_one(".js-save-job-btn")
            jobid = btn.get("data-job-id", "") if btn else ""
            location = ""
            if href and "/job/" in href:
                loc = href.split("/job/")[1].split("/")[0]
                location = loc.replace("-", " ").title()
            jobs.append(Job(
                title=title,
                jobid=jobid,
                company="Citi",
                location=location,
                url=f"https://jobs.citi.com{href}" if href else "",
                posted_date="",
            ))
        return jobs
