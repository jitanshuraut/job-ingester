import re


PLATFORM_PATTERNS = [
    ("workday", r"myworkdayjobs\.com"),
    ("greenhouse", r"(job-boards|boards)\.greenhouse\.io"),
    ("lever", r"jobs\.lever\.co"),
    ("ashby", r"jobs\.ashbyhq\.com"),
    ("icims", r"icims\.com"),
    ("eightfold", r"eightfold\.ai"),
    ("smartrecruiters", r"jobs\.smartrecruiters\.com"),
    ("wellfound", r"wellfound\.com"),
    ("linkedin", r"linkedin\.com/jobs"),
    ("rippling", r"ats\.rippling\.com"),
    ("successfactors", r"successfactors\.(eu|com)"),
    ("oraclecloud", r"fa-[\w]+\.fa\.\w+\.oraclecloud\.com"),
    ("darwinbox", r"darwinbox\.in"),
    ("sensehq", r"sensehq\.in"),
    ("paylocity", r"paylocity\.com"),
    ("hirepro", r"hirepro\.in"),
    ("peoplestrong", r"peoplestrong\.com"),
    ("google", r"google\.com/about/careers"),
    ("kula", r"careers\.kula\.ai"),
    ("mynexthire", r"mynexthire\.com"),
    ("natwest", r"jobs\.natwestgroup\.com"),
    ("siemens", r"jobs\.siemens\.com"),
    ("apple", r"jobs\.apple\.com"),
    ("squarepoint", r"squarepoint-capital\.com"),
    ("towerresearch", r"tower-research\.com"),
]


def categorize(url: str) -> str:
    if not url:
        return "unknown"
    url_lower = url.lower()
    for name, pattern in PLATFORM_PATTERNS:
        if re.search(pattern, url_lower):
            return name
    if "/careers/" in url_lower or "/jobs/" in url_lower or "/job/" in url_lower:
        return "careers_page"
    return "other"


def normalize_workday_url(url: str) -> str:
    url = url.rstrip("/")
    for suffix in ["/apply", "/login", "/signin"]:
        if url.endswith(suffix):
            url = url[: -len(suffix)]
            break
    return url


def get_example_urls(limit_per_platform: int = 3):
    import sqlite3
    conn = sqlite3.connect("data/jobs.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT url, company FROM jobs WHERE url IS NOT NULL AND url != ''"
    ).fetchall()
    conn.close()
    categorized = {}
    for row in rows:
        cat = categorize(row["url"])
        if cat not in categorized:
            categorized[cat] = []
        if len(categorized[cat]) < limit_per_platform:
            categorized[cat].append((row["company"], row["url"]))
    return categorized
