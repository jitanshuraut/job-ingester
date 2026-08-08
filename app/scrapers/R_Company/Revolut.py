import re
import json
from playwright.sync_api import sync_playwright
from app.scrapers.base import BaseScraper
from app.models.job import Job
from app.utils.proxy_manager import current_proxy


class RevolutScraper(BaseScraper):
    CAREERS_URL = "https://www.revolut.com/en-IN/careers/"

    def fetch_raw(self):
        with sync_playwright() as p:
            launch_kwargs = {
                "headless": True,
                "args": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-blink-features=AutomationControlled",
                ],
            }

            browser = p.chromium.launch(**launch_kwargs)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-IN",
            )
            page = context.new_page()
            page.goto(self.CAREERS_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()
            return html

    def parse(self, html: str) -> list[Job]:
        m = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html, re.DOTALL,
        )
        if not m:
            return []
        data = json.loads(m.group(1))
        positions = data.get("props", {}).get("pageProps", {}).get("positions", [])
        return self._build_jobs(positions)

    def fetch_jobs(self) -> list[Job]:
        html = self.fetch_raw()
        return self.parse(html)

    def _build_jobs(self, positions: list) -> list[Job]:
        jobs = []
        for item in positions:
            locs = [loc.get("name", "") for loc in item.get("locations", [])]
            jobs.append(Job(
                title=item.get("text", ""),
                jobid=item.get("id", ""),
                company="Revolut",
                location=", ".join(locs),
                url=self.CAREERS_URL,
                posted_date="",
            ))
        return jobs
