from app.scrapers.base_playwright import PlaywrightScraper
from app.models.job import Job
from bs4 import BeautifulSoup
from app.utils.DateConverter import convert_to_common_format
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright


class NatWestScraper(PlaywrightScraper):
    BASE_URL = "https://jobs.natwestgroup.com/search/technology/jobs/in/country/india"
    TIMEOUT = 60000

    def _new_page(self, browser):
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()
        return page, context

    def _get_page(self, page, url):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=self.TIMEOUT)
            page.wait_for_timeout(2000)
            return page.content()
        except Exception:
            return ""

    def _parse_page(self, html):
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        jobs = []
        for card in soup.select("a.job[data-job-card]"):
            title_el = card.select_one(".job__title")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            location_el = card.select_one(".job__location")
            location = location_el.get_text(strip=True) if location_el else ""
            href = card.get("href", "")
            url = urljoin(self.BASE_URL, href)
            req_el = card.select_one(".job__reference")
            req_id = req_el.get_text(strip=True) if req_el else ""
            date_el = card.select_one(".job__posted-date")
            date_text = date_el.get_text(strip=True) if date_el else ""
            posted = convert_to_common_format(date_text)
            jobs.append(Job(
                title=title,
                company="NatWest",
                location=location,
                url=url,
                jobid=req_id,
                posted_date=posted,
            ))
        return jobs

    def _get_total_pages(self, html):
        if not html:
            return 1
        soup = BeautifulSoup(html, "lxml")
        page_links = soup.select(".pagination a:not(.prev_page):not(.next_page)")
        pages = [int(a.get_text(strip=True)) for a in page_links if a.get_text(strip=True).isdigit()]
        return max(pages) if pages else 1

    def fetch_jobs(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.HEADLESS)
            all_jobs = []

            page1, ctx1 = self._new_page(browser)
            html = self._get_page(page1, self.BASE_URL)
            ctx1.close()

            if not html:
                browser.close()
                return []

            all_jobs.extend(self._parse_page(html))
            total_pages = self._get_total_pages(html)

            for pg in range(2, total_pages + 1):
                page_n, ctx_n = self._new_page(browser)
                html = self._get_page(page_n, f"{self.BASE_URL}?page={pg}")
                ctx_n.close()
                if html:
                    all_jobs.extend(self._parse_page(html))

            browser.close()
            return all_jobs
