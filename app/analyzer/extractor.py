import re
from .constants import TECH_SKILLS

_SKILLS_SORTED = sorted(TECH_SKILLS, key=lambda s: -len(s))
_SKILLS_ALTERNATION = re.compile(
    "|".join(r"(?<![a-zA-Z])" + re.escape(s) + r"(?![a-zA-Z])" for s in _SKILLS_SORTED),
    re.IGNORECASE,
)


def extract_experience_years(text: str) -> list[dict]:
    if not text:
        return []
    results = []
    patterns = [
        # "over 5 years of experience"
        (r"over\s+(\d+)\+?\s*(?:year|yr)s?\s*(?:of\s+)?experience", 1),
        # "experience 5-7 years" (experience BEFORE the range)
        (r"experience\s*(?:of|:)?\s*(\d+)\+?\s*(?:[-–]|\s*to\s*)\s*(\d+)\+?\s*years?", 2),
        # "5-7 years of experience", "5–7 years of experience" (range BEFORE experience)
        (r"(\d+)\s*[-–]+\s*(\d+)\+?\s*(?:year|yr)s?\s*(?:of\s+)?(?:\S+\s+)*?experience", 2),
        # "5-7 years in/as/with/leading" (range, no "experience" required)
        (r"(\d+)\s*[-–]+\s*(\d+)\+?\s*(?:year|yr)s?\s+(?:in|as|with|leading|managing|handling|on)", 2),
        # "minimum 5 years", "minimum of 5 years"
        (r"minimum\s*(?:of\s+)?(\d+)\+?\s*(?:year|yr)s?", 1),
        # "at least 5 years"
        (r"at\s*least\s*(\d+)\+?\s*(?:year|yr)s?", 1),
        # "5+ years of professional/industry/work/demonstrated/proven/progressive experience" (specific qualifiers)
        (r"(\d+)\+?\s*(?:year|yr)s?\s*(?:of\s+)?(?:relevant|professional|industry|work|demonstrated|proven|progressive)", 1),
        # "5 years experience", "5 years' experience", "5 years' experience" (with optional "of" and apostrophe)
        (r"(\d+)\+?\s*(?:year|yr)s?['’]?\s*(?:of\s+)?(?:experience|exp)", 1),
        # "5+ years of ... experience" (general catch-all: any words between years and "experience")
        (r"(\d+)\+?\s*(?:year|yr)s?\s*(?:of\s+)?(?:\S+\s+)*?experience", 1),
        # "8+ years leading/as/managing" (standalone with context verb, no "experience")
        (r"(\d+)\+?\s*(?:year|yr)s?\s+(?:as\s+a\s+|leading|handling|managing)", 1),
        # "8-12 months of experience" (months range)
        (r"(\d+)\s*[-–]+\s*(\d+)\+?\s*(?:month|mo)s?\s*(?:of\s+)?(?:\S+\s+)*?experience", 2),
        # "6 months of experience" (months single)
        (r"(\d+)\+?\s*(?:month|mo)s?\s*(?:of\s+)?(?:\S+\s+)*?experience", 1),
    ]
    for pattern, group_count in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            if group_count == 2:
                y1, y2 = int(match.group(1)), int(match.group(2))
                results.append({
                    "min_years": min(y1, y2),
                    "max_years": max(y1, y2),
                    "text": match.group(0),
                })
            else:
                results.append({
                    "min_years": int(match.group(1)),
                    "max_years": int(match.group(1)),
                    "text": match.group(0),
                })
    results.sort(key=lambda x: x["min_years"])
    return results


def extract_skills(text: str) -> list[str]:
    if not text:
        return []
    found = set(_SKILLS_ALTERNATION.findall(text))
    return sorted(found, key=lambda s: -len(s))


def extract_degree(text: str) -> list[str]:
    if not text:
        return []
    degrees = []
    patterns = [
        r"(?:Bachelor|Master|PhD|Ph\.D|B\.\w+|M\.\w+|B\.Tech|M\.Tech|B\.E|M\.E|B\.S|M\.S|B\.A|M\.A)\s*(?:'s)?(?:\s*(?:degree|in))?",
        r"(?:bachelor|master|phd|doctorate)\s*(?:'s)?\s*(?:degree)?(?:\s+in\s+\w+)?",
    ]
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            degrees.append(m.group(0))
    return degrees


def analyze_job_description(text: str) -> dict:
    return {
        "experience_years": extract_experience_years(text),
        "skills": extract_skills(text),
        "degrees": extract_degree(text),
        "text_length": len(text),
    }
