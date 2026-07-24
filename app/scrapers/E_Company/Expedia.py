from app.scrapers.base_playwright import PlaywrightScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format


class ExpediaScraper(PlaywrightScraper):
    HEADLESS = True
    TIMEOUT = 45000

    INDIA_KEYWORDS = [
        "india", "bangalore", "bengaluru", "gurgaon", "gurugram",
        "hyderabad", "pune", "mumbai", "chennai", "kolkata",
        "noida", "delhi", "ahmedabad", "kochi", "coimbatore",
    ]
    BASE_URL = "https://lifeatexpediagroup.com"

    def fetch_raw(self):
        return self._run_playwright(self._scrape)

    def _scrape(self, page):
        page.goto(
            "https://careers.expediagroup.com/jobs/",
            timeout=self.TIMEOUT, wait_until="domcontentloaded"
        )
        page.wait_for_timeout(5000)
        return page.content()

    @staticmethod
    def _is_india(location_text: str) -> bool:
        loc = location_text.lower().strip()
        if loc.startswith("india") or " - india" in loc:
            return True
        for kw in ExpediaScraper.INDIA_KEYWORDS:
            if kw in loc:
                return True
        return False

    def parse(self, data) -> list[Job]:
        if not data:
            return []
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(data, "lxml")
        jobs = []
        for item in soup.select("li.Results__list__item"):
            link = item.select_one("a.view-job-button")
            if not link:
                continue
            title_el = link.select_one("h3.Results__list__title")
            loc_el = link.select_one("h4.Results__list__location")
            if not title_el or not loc_el:
                continue
            title = title_el.get_text(strip=True)
            location = loc_el.get_text(strip=True)
            if not title or len(title) <= 3:
                continue
            if not self._is_india(location):
                continue
            href = link.get("href", "")
            job_id = ""
            import re
            id_match = re.search(r"/R-(\d+)/", href)
            if id_match:
                job_id = id_match.group(1)
            full_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
            jobs.append(Job(
                title=title,
                jobid=job_id,
                company="Expedia Group",
                location=location,
                url=full_url,
                posted_date="",
            ))
        return jobs
