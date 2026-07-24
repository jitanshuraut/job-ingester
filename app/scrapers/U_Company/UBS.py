from app.scrapers.base_playwright import PlaywrightScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
import re


class UBSScraper(PlaywrightScraper):
    HEADLESS = True
    TIMEOUT = 60000

    def fetch_raw(self):
        return self._run_playwright(self._scrape)

    def _scrape(self, page):
        page.goto(
            "https://jobs.ubs.com/TGnewUI/Search/home/HomeWithPreLoad?PageType=JobSearch&partnerid=25008&siteid=5079&LocationCountry=India",
            timeout=self.TIMEOUT, wait_until="domcontentloaded"
        )
        page.wait_for_timeout(5000)

        for _ in range(10):
            try:
                more = page.get_by_role("button", name=re.compile(r"load more", re.IGNORECASE))
                if more.count() and more.first.is_visible():
                    more.first.click()
                    page.wait_for_timeout(2000)
                else:
                    break
            except Exception:
                break
        return page.content()

    def parse(self, data) -> list[Job]:
        if not data:
            return []
        from bs4 import BeautifulSoup
        import re
        soup = BeautifulSoup(data, "lxml")
        jobs = []
        for card in soup.select("[class*='job'], [data-automation-id*='job'], tr[data-job-id]"):
            title_el = card.select_one("a[href*='job'], h3 a, .job-title a")
            if not title_el:
                title_el = card.select_one("a")
            if title_el:
                title = title_el.get_text(strip=True)
                href = title_el.get("href", "")
                if title and len(title) > 3:
                    full_url = href if href.startswith("http") else f"https://jobs.ubs.com{href}"
                    jobs.append(Job(
                        title=title,
                        jobid="",
                        company="UBS",
                        location="India",
                        url=full_url,
                        posted_date="",
                    ))
        return jobs
