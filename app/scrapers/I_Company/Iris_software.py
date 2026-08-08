import re
from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
from bs4 import BeautifulSoup
from app.utils.DateConverter import convert_to_common_format


class IrisSoftwareScraper(BaseScraper):
    SEARCH_URL = "https://careers.irissoftware.com/search/"
    PAGE_SIZE = 30

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        })

    def _fetch_page(self, startrow: int) -> str:
        params = {
            "createNewAlert": "false",
            "q": "",
            "locationsearch": "india",
            "optionsFacetsDD_customfield1": "",
            "startrow": startrow,
        }
        try:
            response = self._session.get(self.SEARCH_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return ""

    def fetch_raw(self):
        return self._fetch_page(0)

    def fetch_jobs(self) -> list[Job]:
        first = self._fetch_page(0)
        if not first:
            return []
        soup = BeautifulSoup(first, "lxml")
        total = self._parse_total(soup)
        jobs = self._parse_page(first)
        for startrow in range(self.PAGE_SIZE, total, self.PAGE_SIZE):
            html = self._fetch_page(startrow)
            if html:
                jobs.extend(self._parse_page(html))
        return jobs

    def _parse_total(self, soup: BeautifulSoup) -> int:
        label = soup.find("span", id="tile-search-results-label")
        if not label:
            return 0
        match = re.search(r"of (\d+)", label.get_text())
        return int(match.group(1)) if match else 0

    def parse(self, raw) -> list[Job]:
        return self._parse_page(raw)

    def _parse_page(self, html: str) -> list[Job]:
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        job_list = []
        for tile in soup.select("li.job-tile"):
            link = tile.select_one("a.jobTitle-link")
            if not link:
                continue
            title = link.get_text(strip=True)
            href = tile.get("data-url") or link.get("href", "")
            full_url = f"https://careers.irissoftware.com{href}" if href.startswith("/") else href
            jobid = self._field(tile, "customfield1")
            location = self._field(tile, "location")
            date_str = self._field(tile, "date")
            job = Job(
                title=title,
                jobid=jobid,
                company="IrisSoftware",
                location=location,
                url=full_url,
                posted_date=convert_to_common_format(date_str),
            )
            job_list.append(job)
        return job_list

    def _field(self, tile, name: str) -> str:
        node = tile.select_one(f'[id$="-section-{name}-value"]')
        return node.get_text(strip=True) if node else ""