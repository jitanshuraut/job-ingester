from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
from bs4 import BeautifulSoup
from app.utils.DateConverter import convert_to_common_format


class CapitalOneScraper(BaseScraper):
    BASE_URL = "https://www.capitalonecareers.com/search-jobs/software/India/234/1/2/1269750/22/79/50/2"

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
        links = soup.select("li > a[data-job-id]")
        jobs = []
        for a in links:
            h = a.select_one("h2, h3")
            title = h.get_text(strip=True) if h else ""
            jobid = a.get("data-job-id", "")
            loc = a.select_one(".job-location")
            location = loc.get_text(strip=True) if loc else ""
            date_el = a.select_one(".job-date-posted")
            date_str = date_el.get_text(strip=True) if date_el else ""
            href = a.get("href", "")
            jobs.append(Job(
                title=title,
                jobid=jobid,
                company="CapitalOne",
                location=location,
                url=f"https://www.capitalonecareers.com{href}" if href else "",
                posted_date=convert_to_common_format(date_str),
            ))
        return jobs
