from app.scrapers.base_playwright import PlaywrightScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format


class IntuitScraper(PlaywrightScraper):
    HEADLESS = True
    TIMEOUT = 60000

    def fetch_raw(self):
        return self._run_playwright(self._scrape)

    def _scrape(self, page):
        page.goto("https://jobs.intuit.com/search-jobs/software/India/27595/1/2/1269750/22/79/0/2", timeout=self.TIMEOUT, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        try:
            show_all = page.locator("a.pagination-show-all")
            if show_all.count() and show_all.first.is_visible():
                show_all.first.click()
                page.wait_for_timeout(3000)
        except Exception:
            pass
        return page.content()

    def parse(self, data) -> list[Job]:
        if not data:
            return []
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(data, "lxml")
        jobs = []
        for card in soup.select("[data-intuit-jobid]"):
            a = card.select_one("a[data-title]")
            if not a:
                continue
            title = a.get("data-title", "")
            href = a.get("href", "")
            loc_el = a.select_one(".job-location, [class*='location']")
            location = loc_el.get_text(strip=True) if loc_el else ""
            url = f"https://jobs.intuit.com{href}" if href.startswith("/") else href
            if title:
                jobs.append(Job(
                    title=title,
                    jobid=card.get("data-intuit-jobid", ""),
                    company="Intuit",
                    location=location,
                    url=url,
                    posted_date="",
                ))
        return jobs
