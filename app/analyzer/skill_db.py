import json
import re
from pathlib import Path

from .constants import TECH_SKILLS

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_SKILL_DB_PATH = _PROJECT_ROOT / "skill_db_relax_20.json"

INCLUDED_TYPES = ("Hard Skill", "Certification")


def _load_skill_db() -> dict | None:
    try:
        with open(_SKILL_DB_PATH, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return None


SKILL_DB = _load_skill_db()


def _token_sequence_pattern(form: str) -> str:
    tokens = form.split()
    return r"(?<![a-zA-Z0-9])" + r"\W*".join(re.escape(t) for t in tokens) + r"(?![a-zA-Z0-9])"


def _phrase_pattern(form: str) -> str:
    return r"(?<![a-zA-Z])" + re.escape(form) + r"(?![a-zA-Z])"


def _clean_skill_name(name: str) -> str:
    return re.sub(r"\s*\(.*?\)\s*", "", name).strip() or name


_INDEX: dict[str, list[tuple[str, str]]] | None = None


def _build_index() -> dict[str, list[tuple[str, str]]]:
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    _INDEX = {}
    if not SKILL_DB:
        return _INDEX

    for v in SKILL_DB.values():
        if v.get("skill_type") not in INCLUDED_TYPES:
            continue
        skill_name = _clean_skill_name(v.get("skill_name", ""))
        if not skill_name:
            continue
        forms = list(v.get("high_surfce_forms", {}).values()) + v.get("low_surface_forms", [])
        for form in forms:
            form = form.strip()
            if not form:
                continue
            pattern = _token_sequence_pattern(form) if v.get("match_on_tokens") else _phrase_pattern(form)
            first_token = form.split()[0]
            _INDEX.setdefault(first_token, []).append((pattern, skill_name))
    return _INDEX


def _text_tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9+#]+", text.lower()))


def extract_skills_emsi(text: str) -> list[str]:
    if not text or not SKILL_DB:
        return []
    index = _build_index()
    text_lower = text.lower()
    tokens = _text_tokens(text)
    found = set()
    for token in tokens:
        for pattern, skill_name in index.get(token, ()):
            if re.search(pattern, text_lower):
                found.add(skill_name)
    return sorted(found, key=lambda s: (-len(s), s))


def is_emsi_available() -> bool:
    return bool(SKILL_DB)
