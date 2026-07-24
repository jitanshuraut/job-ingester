from app.scrapers.base import BaseScraper
from app.models.job import Job
from playwright.sync_api import sync_playwright
from app.utils.DateConverter import convert_to_common_format
from app.utils.proxy_manager import current_proxy


class PlaywrightScraper(BaseScraper):
    HEADLESS = True
    TIMEOUT = 30000

    def _run_playwright(self, callback):
        with sync_playwright() as p:
            launch_kwargs = {"headless": self.HEADLESS}
            pw_proxy = self._playwright_proxy()
            if pw_proxy:
                launch_kwargs["proxy"] = pw_proxy

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

    def _playwright_proxy(self) -> dict | None:
        p = self.proxy or current_proxy()
        if not p:
            return None
        if p.startswith("socks5://") or p.startswith("socks4://"):
            return {"server": p}
        return {"server": p}
