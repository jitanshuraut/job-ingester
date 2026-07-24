# Job Ingester

Aggregates job postings from **102+ companies** for India locations and sends email notifications. Runs all scrapers, stores results in Supabase (or local SQLite), and provides a web UI with SSE streaming, filtering, and search.

## Features

- **102 scrapers** — BaseScraper (requests+BS4) and PlaywrightScraper (headless browser) for Workday CXS, Greenhouse, Algolia, server-rendered HTML, Next.js RSC, and more
- **India-focused** — each scraper filters jobs to India-based roles (Bangalore, Mumbai, Pune, Hyderabad, Gurugram, remote, etc.)
- **Supabase storage** — all jobs persisted with company, title, location, posted_date, URL
- **Web server** — FastAPI + SSE streaming scrape, job search/filter by company, date range, keyword; runs/dates tracking; applied-job toggle
- **Local SQLite fallback** — operates without Supabase using `app/db/local_db.py`
- **Email notifications** — sends HTML job listings via Gmail SMTP to configurable recipients
- **Proxy rotation** — round-robins through `PROXY_LIST` env var, randomized wait between scrapers
- **Archive** — `archive_old_jobs.sql` moves all rows to `archive` table then truncates `jobs` for a fresh scrape

## Setup

### Prerequisites
- Python 3.8+
- [Playwright browsers](https://playwright.dev/python/docs/library) — run `playwright install chromium` if using Playwright-based scrapers

### Installation
```sh
git clone https://github.com/jitanshuraut/job-ingester.git
cd job-ingester
pip install -r requirements.txt
playwright install chromium   # only needed for Playwright scrapers
```

### Configuration
Create a `.env` file in the project root:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# Email (optional — for main.py notifications)
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# Proxy rotation (optional)
PROXY_LIST=http://proxy1:port,http://proxy2:port

# Random wait between scrapers (optional, defaults 3-8s)
# WAIT_MIN=3
# WAIT_MAX=8
```

## Usage

### Run all scrapers + email
```sh
python main.py
```
Runs all 102 scrapers, inserts new jobs into Supabase, and sends an email digest.

### Test a single scraper
```sh
python test_scraper.py Nvidia
python test_scraper.py BrowserStackScraper
```
Case-insensitive; matches class name or company name.

### Run all scrapers (no email)
```sh
python -c "from app.core.Aggregator import JobAggregator; a=JobAggregator(); jobs=a.run(); print(f'{len(jobs)} jobs')"
```

### Start the web server
```sh
bash start.sh            # start on port 8000
bash start.sh stop       # stop
bash start.sh restart    # restart
```

The web UI is at `http://localhost:8000` with:
- Live streaming scrape (`POST /api/scrape` or SSE at `/api/scrape/stream`)
- Job search & filter (`GET /api/jobs?company=NVIDIA&search=engineer&sort_by=date&limit=50`)
- Company counts (`GET /api/companies/counts`)
- Scrape run history (`GET /api/runs`, `GET /api/runs/dates`)
- Applied-job toggle (`GET /api/jobs/toggle-applied?job_key=company|jobid`)

### Archive jobs before fresh scrape
```sh
# Moves all jobs to archive table and truncates jobs
# Run manually when needed
psql "$SUPABASE_DATABASE_URL" -f archive_old_jobs.sql
```

## Project Structure
```
job-ingester/
├── app/
│   ├── core/
│   │   └── Aggregator.py        # Discovers and runs all scrapers
│   ├── db/
│   │   ├── local_db.py          # SQLite fallback (jobs, runs, applied)
│   │   └── db_client.py         # Supabase client
│   ├── emailer/
│   │   └── emailer.py           # Gmail SMTP sender + HTML templates
│   ├── models/
│   │   └── job.py               # Job dataclass
│   ├── scrapers/
│   │   ├── base.py              # BaseScraper (requests)
│   │   ├── base_playwright.py   # PlaywrightScraper
│   │   └── {X}_Company/         # One directory per letter
│   │       ├── CompanyA.py
│   │       └── ...
│   ├── utils/
│   │   ├── DateConverter.py     # Relative date, MM/DD/YYYY, ms timestamps
│   │   └── proxy_manager.py     # Round-robin proxy + random_wait
│   └── web/
│       ├── server.py            # FastAPI app (SSE streaming, REST API)
│       └── static/              # Frontend assets
├── main.py                      # Scrape + email entry point
├── test_scraper.py              # Single-scraper test runner
├── start.sh                     # uvicorn server lifecycle
├── archive_old_jobs.sql         # Archive + truncate jobs table
├── requirements.txt
└── .env
```

## Adding a New Scraper

1. Create `app/scrapers/{X}_Company/CompanyName.py`
2. Extend `BaseScraper` (requests+BS4) or `PlaywrightScraper` (headless browser)
3. Implement `fetch_jobs()` returning a `list[Job]`
4. It's auto-discovered by `JobAggregator.discover_scrapers()`

```python
from app.scrapers.base import BaseScraper
from app.models.job import Job

class ExampleScraper(BaseScraper):
    def fetch_jobs(self) -> list[Job]:
        # ... fetch and parse jobs
        return [Job(title="...", jobid="...", company="Example",
                    location="...", url="...", posted_date="...")]
```

## Supported Companies (102)

Able, Acko, Adobe, Agoda, Airbus, AirtelLabs, Akamai, Allianz, Amadeus, Amazon, Amdocs, AMD, AmericanExpress, AnalogDevices, AppDynamics, Apple, Aspora, Autodesk, BNY, BrowserStack, Cadence, CapitalOne, Cashfree, Cisco, Citi, CrowdStrike, Cvent, Dell, Ericsson, Expedia, F5, FICO, GEHealthCare, Genpact, GEVernova, GlobalPayments, GoldmanSachs, Google, Granica, Graviton, Harness, HPE, IBM, Innovaccer, InteractiveBrokers, Intuit, iRage, JioStar, JPMorgan, Juniper, Lowes, LSEG, Mastercard, Microsoft, Morningstar, MSCI, Nasdaq, NatWest, NetApp, NewRelic, Nexthink, Nutanix, NVIDIA, Oracle, Payoneer, PayPal, Paytm, PayU, PhonePe, Proofpoint, PropertyGuru, Qualcomm, Quantiphi, RedHat, Rippling, Salesforce, ServiceNow, Siemens, SLB, Sprinklr, SquarepointCapital, Swiggy, Synopsys, Target, Tekion, TeraData, Tesco, TexasInstruments, Thoughtspot, Thoughtworks, TowerResearch, Uber, UBS, UKG, Unisys, Visa, WarnerBros, WellsFargo, Yugabyte, CareerZenith, Zeta, ZS

## License

MIT
