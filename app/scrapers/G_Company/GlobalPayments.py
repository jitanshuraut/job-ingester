from app.scrapers.base_playwright import PlaywrightScraper
from app.models.job import Job
from app.utils.DateConverter import convert_to_common_format
from bs4 import BeautifulSoup


class GlobalPaymentsScraper(PlaywrightScraper):
    BASE_URL = "https://jobs.globalpayments.com/jobs?locations=India%7C%7CBengaluru&locations=India%7C%7CIndore&locations=India%7C%7CPune"
    TIMEOUT = 60000

    def fetch_jobs(self):
        def callback(page):
            page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=self.TIMEOUT)
            page.wait_for_timeout(5000)

            for _ in range(30):
                try:
                    btn = page.query_selector("button:has-text('Load More')")
                    if not btn or not btn.is_visible():
                        break
                    btn.click()
                    page.wait_for_timeout(1500)
                except Exception:
                    break

            html = page.content()
            return self._parse(html)

        return self._run_playwright(callback)

    def _parse(self, html: str) -> list[Job]:
        soup = BeautifulSoup(html, "lxml")
        jobs = []
        seen = set()
        for card in soup.select(".JobListing_jobListing__c6Qw0"):
            link = card.select_one("a[href*='/jobs/']")
            if not link:
                continue
            href = link.get("href", "")
            if href in seen:
                continue
            seen.add(href)

            title_el = card.select_one('[itemprop="title"]')
            title = title_el.get_text(strip=True) if title_el else ""

            paragraphs = card.select(".JobListing_text__Y4Gjt p")
            team = paragraphs[1].get_text(strip=True) if len(paragraphs) >= 2 else ""
            job_id = paragraphs[2].get_text(strip=True) if len(paragraphs) >= 3 else ""
            loc_el = paragraphs[3].select_one("span") if len(paragraphs) >= 4 else None
            location = loc_el.get_text(strip=True) if loc_el else ""

            if not title:
                continue

            jobs.append(Job(
                title=title,
                jobid=job_id,
                company="Global Payments",
                location=location,
                url=f"https://jobs.globalpayments.com{href}",
                posted_date="",
            ))
        return jobs
