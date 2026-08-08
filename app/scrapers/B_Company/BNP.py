from app.scrapers.base import BaseScraper
from app.models.job import Job
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


class BNPScraper(BaseScraper):
    BASE = "https://group.bnpparibas"
    LIST_URL = f"{BASE}/en/careers/all-job-offers"
    DOMAIN = "168|6"
    COUNTRY = "47"

    def fetch_raw(self):
        all_jobs = []
        page = 1
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Chrome/150.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        while True:
            params = {"page": page, "domain": self.DOMAIN, "country": self.COUNTRY}
            resp = requests.get(self.LIST_URL, params=params, headers=headers, timeout=15)
            if resp.status_code != 200:
                break
            soup = BeautifulSoup(resp.text, "html.parser")
            articles = soup.select("article.card-offer")
            if not articles:
                break
            for art in articles:
                title_el = art.select_one("h3")
                loc_el = art.select_one(".offer-location")
                link_el = art.select_one("a.card-link")
                all_jobs.append({
                    "title": title_el.get_text(strip=True) if title_el else "",
                    "location": loc_el.get_text(strip=True) if loc_el else "",
                    "url": urljoin(self.BASE, link_el.get("href", "")) if link_el else "",
                })
            page += 1
            if not soup.select_one("li.next a"):
                break
        return all_jobs

    def parse(self, raw) -> list[Job]:
        return [
            Job(
                title=j["title"],
                jobid="",
                company="BNP Paribas",
                location=j["location"],
                url=j["url"],
                posted_date="",
            )
            for j in raw
        ]
