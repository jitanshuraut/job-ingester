from app.scrapers.base import BaseScraper
from app.models.job import Job
from playwright.sync_api import sync_playwright
from app.utils.DateConverter import convert_to_common_format
class PlaywrightScraper(BaseScraper):
    HEADLESS = True
    TIMEOUT = 30000

    def _run_playwright(self, callback):
        with sync_playwright() as p:
            launch_kwargs = {
                "headless": self.HEADLESS,
                "args": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            }
            browser = p.chromium.launch(**launch_kwargs)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
            )
            page = context.new_page()
            try:
                result = callback(page)
            finally:
                browser.close()
            return result
