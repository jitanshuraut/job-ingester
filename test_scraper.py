import sys
import importlib
import inspect
import json
from app.scrapers.base import BaseScraper

if len(sys.argv) < 2:
    print("Usage: python test_scraper.py <ScraperName or CompanyName>")
    print("Example: python test_scraper.py AllianzScraper")
    print("         python test_scraper.py Irage")
    sys.exit(1)

query = sys.argv[1].lower()

# Search all company directories for the matching scraper
from app.core.Aggregator import JobAggregator
agg = JobAggregator()
scrapers = agg.discover_scrapers()

target = None
for s in scrapers:
    name = s.__class__.__name__.lower()
    if query == name or query == name.replace("scraper", "") or query in name:
        target = s
        break

if not target:
    print(f"❌ No scraper found matching '{query}'")
    print(f"   Available: {', '.join(s.__class__.__name__ for s in scrapers)}")
    sys.exit(1)

cls_name = target.__class__.__name__
print(f"🔍 Running {cls_name}...")
print(f"{'='*60}")

import time
start = time.time()

try:
    jobs = target.fetch_jobs()
    print("\nEnriching with experience & skills from job descriptions...")
    target.enrich_jobs(jobs)
    elapsed = time.time() - start
    print(f"\n✅ {cls_name}: {len(jobs)} jobs in {elapsed:.1f}s")
    print(f"{'─'*160}")
    for j in jobs:
        loc = j.location or "—"
        jid = str(j.jobid) if j.jobid is not None else "—"
        pd = str(j.posted_date) if j.posted_date else "—"
        try:
            exp_list = json.loads(j.experience_years) if j.experience_years else []
        except (json.JSONDecodeError, TypeError):
            exp_list = []
        exp = ", ".join(f"{e.get('min_years')}-{e.get('max_years')}y" for e in exp_list[:3]) or "—"
        try:
            skill_list = json.loads(j.skills) if j.skills else []
        except (json.JSONDecodeError, TypeError):
            skill_list = []
        skills = ", ".join(skill_list[:8]) or "—"
        print(f"  {j.title[:60]:60s} | {loc[:25]:25s} | {jid[:10]:10s} | {pd[:10]:10s} | exp: {exp[:18]:18s} | skills: {skills[:40]}")
except Exception as e:
    elapsed = time.time() - start
    print(f"\n❌ {cls_name} FAILED after {elapsed:.1f}s: {e}")
    import traceback
    traceback.print_exc()
