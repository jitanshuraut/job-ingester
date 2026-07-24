from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
from bs4 import BeautifulSoup
import requests
import re


class TescoScraper(BaseScraper):
    BASE_URL = "https://careers.tesco.com/en_GB/careers/SearchJobs/"
    PARAMS = {
        "12328": "[587056]",
        "12328_format": "25911",
        "59964": "[4196244]",
        "59964_format": "26080",
        "listFilterMode": "1",
        "jobRecordsPerPage": "10",
    }

    def _fetch_page(self, offset: int) -> str:
        params = dict(self.PARAMS)
        if offset:
            params["jobOffset"] = str(offset)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }
        try:
            r = requests.get(self.BASE_URL, params=params, headers=headers, timeout=30)
            return r.text
        except requests.RequestException:
            return ""

    def _get_total_results(self, html: str) -> int:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text()
        m = re.search(r"(\d+)\s*[Rr]esults?", text)
        return int(m.group(1)) if m else 0

    def _parse_page(self, html: str) -> list[Job]:
        soup = BeautifulSoup(html, "lxml")
        jobs = []
        for article in soup.find_all("article", class_="article--result"):
            title_el = article.select_one("h3 a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            jobid = href.rstrip("/").rsplit("/", 1)[-1] if "/" in href else ""
            subtitle = article.select_one(".article__header__text__subtitle")
            location = ""
            date_text = ""
            if subtitle:
                loc_el = subtitle.select_one(".list-item-location")
                if loc_el:
                    location = loc_el.get_text(strip=True)
                date_el = subtitle.select_one(".list-item-closingDate")
                if date_el:
                    raw = date_el.get_text(strip=True)
                    date_text = raw.replace("Apply by ", "")
            posted = convert_to_common_format(date_text) if date_text else ""
            jobs.append(Job(
                title=title,
                jobid=jobid,
                company="Tesco",
                location=location,
                url=href,
                posted_date=posted,
            ))
        return jobs

    def fetch_jobs(self) -> list[Job]:
        html = self._fetch_page(0)
        if not html:
            return []
        all_jobs = self._parse_page(html)
        total = self._get_total_results(html)
        per_page = 10
        for offset in range(per_page, total, per_page):
            page_html = self._fetch_page(offset)
            if page_html:
                all_jobs.extend(self._parse_page(page_html))
        return all_jobs
