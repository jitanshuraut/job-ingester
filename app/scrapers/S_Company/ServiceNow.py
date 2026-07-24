import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format


class ServiceNowScraper(BaseScraper):
    LISTING_URL = "https://careers.servicenow.com/jobs/"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    def _fetch_listing(self, params: dict) -> str:
        try:
            r = requests.get(self.LISTING_URL, params=params, headers=self.HEADERS, timeout=30)
            r.raise_for_status()
            return r.text
        except requests.RequestException:
            return ""

    def _parse_listing(self, html: str) -> list[dict]:
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        jobs = []
        for card in soup.select("div.card.card-job"):
            title_el = card.select_one("h2.card-title a.stretched-link")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            actions = card.select_one("[data-id]")
            job_id = actions.get("data-id", "") if actions else ""
            meta_items = card.select(".job-meta li")
            location = meta_items[0].get_text(strip=True) if meta_items else ""
            url = f"https://careers.servicenow.com{href}" if href else ""
            jobs.append({"id": job_id, "title": title, "location": location, "url": url})
        return jobs

    def _fetch_date(self, url: str) -> str:
        try:
            r = requests.get(url, headers=self.HEADERS, timeout=30)
            soup = BeautifulSoup(r.text, "lxml")
            for script in soup.find_all("script", type="application/ld+json"):
                data = json.loads(script.string)
                posted = data.get("datePosted") or ""
                if posted:
                    return convert_to_common_format(posted)
            time_el = soup.find("time")
            if time_el:
                return convert_to_common_format(time_el.get_text(strip=True))
        except Exception:
            pass
        return ""

    def fetch_jobs(self) -> list[Job]:
        all_jobs = []
        page = 1
        while True:
            html = self._fetch_listing({
                "search": "software",
                "country": "India",
                "pagesize": 20,
                "page": page,
            })
            jobs = self._parse_listing(html)
            if not jobs:
                break
            all_jobs.extend(jobs)
            if len(jobs) < 20:
                break
            page += 1

        with ThreadPoolExecutor(max_workers=8) as pool:
            fut_to_job = {pool.submit(self._fetch_date, j["url"]): j for j in all_jobs}
            for fut in as_completed(fut_to_job):
                fut_to_job[fut]["posted_date"] = fut.result()

        return [
            Job(
                title=j["title"],
                jobid=j["id"],
                company="ServiceNow",
                location=j["location"],
                url=j["url"],
                posted_date=j["posted_date"],
            )
            for j in all_jobs
        ]
