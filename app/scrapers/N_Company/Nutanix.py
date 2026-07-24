import requests
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models.job import Job


class NutanixScraper(BaseScraper):
    BASE_URL = "https://careers.nutanix.com/en/jobs/"

    def fetch_jobs(self) -> list[Job]:
        all_jobs = []
        page = 1
        while True:
            url = f"{self.BASE_URL}?page={page}&country=India&search=software&origin=global"
            if page == 1:
                url = f"{self.BASE_URL}?country=India&search=software&origin=global"
            r = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            if r.status_code != 200:
                break
            jobs = self.parse(r.text)
            if not jobs:
                break
            all_jobs.extend(jobs)
            has_next = 'rel="next' in r.text
            if not has_next:
                break
            page += 1
        return all_jobs

    def parse(self, data) -> list[Job]:
        if not data:
            return []
        soup = BeautifulSoup(data, "lxml")
        jobs = []
        for card in soup.select("div.card-job"):
            title_el = card.select_one("h2.card-title a")
            loc_el = card.select_one("p.job-meta-location")
            id_el = card.select_one("p.reference-number")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            full_url = f"https://careers.nutanix.com{href}" if href.startswith("/") else href
            job_id = id_el.get_text(strip=True) if id_el else card.get("data-id", "")
            location = loc_el.get_text(strip=True) if loc_el else "India"
            jobs.append(Job(
                title=title,
                jobid=job_id,
                company="Nutanix",
                location=location,
                url=full_url,
                posted_date="",
            ))
        return jobs
