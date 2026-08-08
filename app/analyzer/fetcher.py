from app.analyzer.categorizer import categorize, normalize_workday_url
import json
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def fetch_description_text(url: str, proxy: str | None = None) -> str:
    if not url or url.startswith("/"):
        return ""
    if categorize(url) == "workday":
        url = normalize_workday_url(url)
    try:
        import requests
        kwargs = {"headers": HEADERS, "timeout": 30, "allow_redirects": True}
        if proxy:
            kwargs["proxies"] = {"http": proxy, "https": proxy}
            kwargs["timeout"] = 10
        r = requests.get(url, **kwargs)
        if r.status_code != 200:
            return ""
        desc = _extract_jsonld_description(r.text)
        if desc:
            return desc
        return _extract_text_from_html(r.text)
    except Exception as e:
        if proxy:
            logger.debug(f"proxy fetch failed for {url}: {e}; retrying direct")
            return fetch_description_text(url, proxy=None)
        logger.warning(f"fetch failed for {url}: {e}")
        return ""


def _extract_jsonld_description(html: str) -> str | None:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                desc = data.get("description") or ""
                if len(desc) > 100:
                    return desc
        except (json.JSONDecodeError, TypeError):
            continue
    return None


def _extract_text_from_html(html: str) -> str:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "meta", "link", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return "\n".join(lines)
