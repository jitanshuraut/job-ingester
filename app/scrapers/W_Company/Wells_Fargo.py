from app.scrapers.base import BaseScraper
from app.models.job import Job
import requests
from bs4 import BeautifulSoup
from app.utils.DateConverter import convert_to_common_format


class WellsFargoScraper(BaseScraper):
    PAGE_SIZE = 100

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })

    def _fetch_page(self, page: int = 1) -> list[dict]:
        url = "https://www.wellsfargojobs.com/en/jobs/"
        params = {
            "country": "India",
            "team": "Technology",
            "pagesize": self.PAGE_SIZE,
            "page": page,
        }
        try:
            response = self._session.get(url, params=params, timeout=30)
            print(response.status_code)
            response.raise_for_status()
            return self._parse_html(response.text)
        except requests.RequestException:
            print(f"Request failed")
            return []

    def fetch_raw(self):
        all_items = []
        page = 1
        while True:
            items = self._fetch_page(page)
            if not items:
                break
            all_items.extend(items)
            page += 1
            if len(items) < 50:
                break
        return all_items

    def fetch_jobs(self) -> list[Job]:
        raw = self.fetch_raw()
        return self.parse(raw)

    def parse(self, data) -> list[Job]:
        return [Job(
            title=item.get("title", ""),
            jobid=item.get("jobid"),
            company="WellsFargo",
            location=item.get("location", ""),
            url=item.get("url", ""),
            posted_date=item.get("posted_date", ""),
        ) for item in data]

    def _parse_html(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("div.card.card-job")
        jobs = []
        for card in cards:
            title_el = card.select_one("h2.card-title a.stretched-link")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            jobid = ""
            actions = card.select_one("[data-id]")
            if actions:
                jobid = actions.get("data-id", "")
            meta_items = card.select(".job-meta li")
            location = meta_items[0].get_text(strip=True) if meta_items else ""
            full_url = f"https://www.wellsfargojobs.com{href}" if href else ""
            jobs.append({
                "title": title,
                "jobid": jobid,
                "location": location,
                "url": full_url,
                "posted_date": "",
            })
        return jobs
