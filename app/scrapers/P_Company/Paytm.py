from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
from bs4 import BeautifulSoup
from app.utils.DateConverter import convert_to_common_format


class PaytmScraper(BaseScraper):
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })

    def fetch_raw(self):
        url = "https://jobs.lever.co/paytm"
        params = {"department": "Technology"}
        try:
            response = self._session.get(url, params=params, timeout=30)
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
        postings = soup.select(".posting")
        job_list = []
        for posting in postings:
            link = posting.select_one("a.posting-title")
            if not link:
                continue
            title_el = link.select_one("h5")
            title = title_el.get_text(strip=True) if title_el else ""
            href = link.get("href", "")
            jobid = posting.get("data-qa-posting-id", "")
            if not jobid:
                jobid = href.rstrip("/").split("/")[-1] if href else ""
            categories = link.select_one(".posting-categories")
            location = ""
            if categories:
                loc_el = categories.select_one(".location")
                location = loc_el.get_text(strip=True) if loc_el else ""
            job = Job(
                title=title,
                jobid=jobid,
                company="Paytm",
                location=location,
                url=href,
                posted_date="",
            )
            job_list.append(job)
        return job_list
