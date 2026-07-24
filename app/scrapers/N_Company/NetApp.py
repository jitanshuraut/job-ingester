from app.scrapers.base import BaseScraper
from app.models.job import Job
import re
import requests
from bs4 import BeautifulSoup
from app.utils.DateConverter import convert_to_common_format


class NetAppScraper(BaseScraper):
    BASE_URL = "https://careers.netapp.com/search-jobs/India"

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })

    def fetch_raw(self):
        return self._fetch_page(1)

    def _fetch_page(self, page: int) -> str:
        params = {"orgIds": "27600", "alp": "1269750", "alt": "2"}
        if page > 1:
            params["p"] = page
        try:
            r = self._session.get(self.BASE_URL, params=params, timeout=30)
            return r.text
        except requests.RequestException:
            return ""

    def _get_total_pages(self, html: str) -> int:
        m = re.search(r'class="pagination-total-pages">of (\d+)', html)
        return int(m.group(1)) if m else 1

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(1)
        if not first:
            return []
        total_pages = self._get_total_pages(first)
        all_jobs = self.parse(first)
        for page in range(2, total_pages + 1):
            html = self._fetch_page(page)
            if html:
                all_jobs.extend(self.parse(html))
        return all_jobs

    def parse(self, html: str) -> list[Job]:
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        job_list = []
        for link in soup.select("li > a[data-job-id]"):
            title_el = link.select_one("h3")
            title = title_el.get_text(strip=True) if title_el else ""
            href = link.get("href", "")
            jobid = link.get("data-job-id", "")
            location_el = link.select_one("span.job-location")
            location = location_el.get_text(strip=True) if location_el else ""
            if not title:
                continue
            full_url = f"https://careers.netapp.com{href}" if href else ""
            job_list.append(Job(
                title=title,
                jobid=jobid,
                company="NetApp",
                location=location,
                url=full_url,
                posted_date="",
            ))
        return job_list
