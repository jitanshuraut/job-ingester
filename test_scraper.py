import sys
import importlib
import inspect
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
    elapsed = time.time() - start
    print(f"\n✅ {cls_name}: {len(jobs)} jobs in {elapsed:.1f}s")
    print(f"{'─'*126}")
    for j in jobs:
        loc = j.location or "—"
        jid = str(j.jobid) if j.jobid is not None else "—"
        pd = str(j.posted_date) if j.posted_date else "—"
        print(f"  {j.title[:70]:70s} | {loc[:30]:30s} | {jid[:36]:36s} | {pd}")
except Exception as e:
    elapsed = time.time() - start
    print(f"\n❌ {cls_name} FAILED after {elapsed:.1f}s: {e}")
    import traceback
    traceback.print_exc()
