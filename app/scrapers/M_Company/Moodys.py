from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests
from bs4 import BeautifulSoup
from datetime import datetime


class MoodysScraper(BaseScraper):
    BASE_URL = "https://careers.moodys.com/en/search-jobs/India/49841/2/1269750/22/79/50/2"

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })

    def fetch_jobs(self) -> list[Job]:
        try:
            r = self._session.get(self.BASE_URL, timeout=30)
            r.raise_for_status()
        except requests.RequestException:
            return []
        soup = BeautifulSoup(r.text, "lxml")
        items = soup.select("li.search-results-list__item")
        jobs = []
        for item in items:
            link = item.select_one("a.search-results-list__job-link")
            if not link:
                continue
            title = link.get_text(strip=True)
            href = link.get("href", "")
            jobid = link.get("data-job-id", "")
            loc_el = item.select_one("li.job-location")
            location = loc_el.get_text(strip=True) if loc_el else ""
            full_url = f"https://careers.moodys.com{href}" if href else ""
            jobs.append(Job(
                title=title,
                jobid=jobid,
                company="Moodys",
                location=location,
                url=full_url,
                posted_date=convert_to_common_format(datetime.now()),
            ))
        return jobs
