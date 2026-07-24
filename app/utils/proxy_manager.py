import os
import random
from itertools import cycle
from dotenv import load_dotenv

load_dotenv()


def _parse_proxy_list() -> list[str]:
    raw = os.getenv("PROXY_LIST", "")
    if raw:
        return [p.strip() for p in raw.split(",") if p.strip()]
    single = os.getenv("HTTP_PROXY", "") or os.getenv("HTTPS_PROXY", "")
    if single:
        return [single]
    return []


PROXIES = _parse_proxy_list()
_cycle = cycle(PROXIES) if PROXIES else None
_current = [None]


def has_proxies() -> bool:
    return len(PROXIES) > 0


def proxy_count() -> int:
    return len(PROXIES)


def next_proxy() -> str | None:
    if not _cycle:
        return None
    _current[0] = next(_cycle)
    return _current[0]


def current_proxy() -> str | None:
    return _current[0]


def random_proxy() -> str | None:
    if not PROXIES:
        return None
    _current[0] = random.choice(PROXIES)
    return _current[0]


def proxy_dict() -> dict | None:
    p = current_proxy()
    if not p:
        return None
    return {"http": p, "https": p}


def wait_min_max() -> tuple[float, float]:
    import ast
    raw_min = os.getenv("WAIT_MIN", "3")
    raw_max = os.getenv("WAIT_MAX", "8")
    try:
        wmin = float(raw_min)
        wmax = float(raw_max)
    except (ValueError, TypeError):
        wmin, wmax = 3.0, 8.0
    return max(wmin, 0.5), max(wmax, wmin + 0.5)


def random_wait() -> float:
    lo, hi = wait_min_max()
    return random.uniform(lo, hi)
