from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import requests
from bs4 import BeautifulSoup
from datetime import datetime


class BloombergScraper(BaseScraper):
    BASE_URL = "https://bloomberg.avature.net/careers/SearchJobs"
    JOBS_PER_PAGE = 100

    INDIA_LOCATIONS = ["162478", "162575", "162477"]

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })

    def fetch_jobs(self) -> list[Job]:
        params = {
            "1845": "[162478,162575,162477]",
            "1845_format": "3996",
            "listFilterMode": "1",
            "jobRecordsPerPage": str(self.JOBS_PER_PAGE),
        }
        try:
            r = self._session.get(self.BASE_URL, params=params, timeout=30)
            r.raise_for_status()
        except requests.RequestException:
            return []
        soup = BeautifulSoup(r.text, "lxml")
        articles = soup.select("article.article--result")
        jobs = []
        for article in articles:
            title_el = article.select_one(".article__header__text__title a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            if not href:
                continue
            loc_el = article.select_one(".list-item-location")
            location = loc_el.get_text(strip=True) if loc_el else ""
            jobid = href.rstrip("/").split("/")[-1]
            jobs.append(Job(
                title=title,
                jobid=jobid,
                company="Bloomberg",
                location=location,
                url=href,
                posted_date=convert_to_common_format(datetime.now()),
            ))
        return jobs
