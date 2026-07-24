from app.scrapers.base_playwright import PlaywrightScraper
from app.models.job import Job
from bs4 import BeautifulSoup


class AgodaScraper(PlaywrightScraper):
    BASE_URL = "https://careersatagoda.com/vacancies/?country=india"
    TIMEOUT = 60000

    def fetch_jobs(self):
        def callback(page):
            page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=self.TIMEOUT)
            page.wait_for_timeout(8000)

            for _ in range(20):
                try:
                    btn = page.query_selector(".js-show-more-job-cards")
                    if not btn or not btn.is_visible():
                        break
                    btn.click()
                    page.wait_for_timeout(800)
                except Exception:
                    break

            html = page.content()
            return self._parse(html)

        return self._run_playwright(callback)

    def _parse(self, html: str) -> list[Job]:
        soup = BeautifulSoup(html, "lxml")
        jobs = []
        for card in soup.find_all("article", class_="caa-job-card"):
            link = card.find("a")
            href = link.get("href", "") if link else ""
            title_el = card.find("h3")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                continue

            icon_text = card.find("div", class_="icon-text")
            location = ""
            if icon_text:
                ps = icon_text.find_all("p")
                if len(ps) >= 1:
                    loc_span = ps[0].find("span")
                    if loc_span:
                        location = loc_span.get_text(strip=True)

            job_id = href.rstrip("/").split("/")[-1].split("-")[0] if href else ""
            jobs.append(Job(
                title=title,
                jobid=job_id,
                company="Agoda",
                location=location,
                url=href,
                posted_date="",
            ))
        return jobs
