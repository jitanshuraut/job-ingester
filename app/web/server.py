from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client
from app.core.Aggregator import JobAggregator
from dataclasses import asdict
from collections import Counter
import json
import os

load_dotenv()

from app.db.local_db import init_db, init_scrape_runs, init_applied_jobs
init_db()
init_scrape_runs()
init_applied_jobs()

app = FastAPI(title="Job Ingester")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_supabase = None


def get_supabase():
    global _supabase
    if os.getenv("USE_SUPABASE", "true").lower() not in ("1", "true", "yes"):
        _supabase = None
        return None
    if _supabase is not None:
        return _supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")
    if url and key:
        try:
            _supabase = create_client(url, key)
            _supabase.table("jobs").select("count", count="exact").limit(1).execute()
        except Exception as e:
            print(f"Supabase connection failed: {e}")
            _supabase = None
    return _supabase


def get_local_db():
    from app.db.local_db import get_jobs, get_companies

    return get_jobs, get_companies


@app.get("/api/scrape/stream")
def scrape_stream(request: Request):
    from queue import Queue
    from threading import Thread

    q: Queue = Queue()
    result = {}

    def run_aggregator():
        try:
            aggregator = JobAggregator(log_fn=lambda m: q.put(("log", m)))
            q.put(("log", "Starting scrapers..."))
            jobs = aggregator.run()
            result["jobs"] = [asdict(j) for j in jobs]
            result["total"] = len(jobs)
            q.put(("done", None))
        except Exception as e:
            q.put(("error", str(e)))

    Thread(target=run_aggregator, daemon=True).start()

    def generate():
        while True:
            kind, payload = q.get()
            if kind == "log":
                yield f"data: {json.dumps({'type': 'log', 'message': payload})}\n\n"
            elif kind == "done":
                yield f"data: {json.dumps({'type': 'done', 'jobs': result.get('jobs', []), 'total': result.get('total', 0)})}\n\n"
                break
            elif kind == "error":
                yield f"data: {json.dumps({'type': 'error', 'message': payload})}\n\n"
                break

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/scrape")
def run_scrapers():
    aggregator = JobAggregator()
    new_jobs = aggregator.run()
    return {"jobs": [asdict(j) for j in new_jobs], "total": len(new_jobs)}


@app.post("/api/jobs/post-telegram")
def post_jobs_telegram(payload: dict):
    from app.telegram.telegram_bot import TelegramBot
    from app.models.job import Job

    try:
        bot = TelegramBot()
    except Exception as e:
        return {"ok": False, "error": f"Telegram not configured: {e}"}

    jobs_data = payload.get("jobs", [])
    jobs = []
    for j in jobs_data:
        try:
            jobs.append(Job(
                title=j.get("title", ""),
                jobid=j.get("jobid", ""),
                company=j.get("company", ""),
                location=j.get("location", ""),
                url=j.get("url", ""),
                posted_date=str(j.get("posted_date") or ""),
            ))
        except Exception:
            continue
    result = bot.send_jobs(jobs)
    return result


def _enrich_with_analysis(jobs_list: list[dict]) -> list[dict]:
    from app.db.local_db import get_connection
    conn = get_connection()
    for j in jobs_list:
        url = j.get("url", "")
        if url:
            row = conn.execute(
                "SELECT ja.experience_years, ja.skills FROM jobs "
                "LEFT JOIN job_analysis ja ON jobs.id = ja.job_id WHERE jobs.url = ?",
                (url,),
            ).fetchone()
            if row:
                j["experience_years"] = row["experience_years"] or ""
                j["skills"] = row["skills"] or ""
    conn.close()
    return jobs_list


@app.post("/api/jobs/post-latest-new")
def post_latest_new_telegram():
    from app.telegram.telegram_bot import TelegramBot
    from app.models.job import Job

    try:
        bot = TelegramBot()
    except Exception as e:
        return {"ok": False, "error": f"Telegram not configured: {e}"}

    from app.db.local_db import get_runs, get_run_jobs
    runs, _ = get_runs(limit=1, offset=0)
    if not runs:
        return {"ok": False, "error": "No runs found"}
    run_id = runs[0]["id"]
    jobs_data, _ = get_run_jobs(run_id, limit=99999, offset=0)
    new_jobs_data = [j for j in jobs_data if j.get("was_new")]
    _enrich_with_analysis(new_jobs_data)

    jobs = []
    for j in new_jobs_data:
        try:
            jobs.append(Job(
                title=j.get("title", ""),
                jobid=j.get("jobid", ""),
                company=j.get("company", ""),
                location=j.get("location", ""),
                url=j.get("url", ""),
                posted_date=str(j.get("posted_date") or ""),
                experience_years=j.get("experience_years", ""),
                skills=j.get("skills", ""),
            ))
        except Exception:
            continue

    result = bot.send_jobs(jobs)
    result["count"] = len(jobs)
    return result


app.mount("/static", StaticFiles(directory="app/web/static"), name="static")


@app.get("/")
async def root():
    return FileResponse("app/web/static/index.html")


@app.get("/api/jobs")
async def jobs_endpoint(
    company: str = Query(None),
    search: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    created_after: str = Query(None),
    created_before: str = Query(None),
    sort_by: str = Query("date"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    sb = get_supabase()
    if sb:
        query = sb.table("jobs").select("*", count="exact")
        if sort_by == "date":
            query = query.order("posted_date", desc=True, nullsfirst=False).order("created_at", desc=True)
        else:
            query = query.order("created_at", desc=True).order("posted_date", desc=True)
        if company:
            query = query.eq("company", company)
        if search:
            query = query.or_(
                f"title.ilike.%{search}%,company.ilike.%{search}%,location.ilike.%{search}%"
            )
        if start_date:
            query = query.gte("posted_date", start_date)
        if end_date:
            query = query.lte("posted_date", end_date)
        if created_after:
            query = query.gte("created_at", created_after)
        if created_before:
            query = query.lte("created_at", created_before)

        response = query.range(offset, offset + limit - 1).execute()
        return {"jobs": response.data, "total": response.count}

    all_jobs, total = get_local_db()[0](
        company=company, search=search, start_date=start_date, end_date=end_date,
        limit=limit, offset=offset,
    )
    return {"jobs": all_jobs, "total": total}


def _fetch_all_companies(sb):
    PAGE_SIZE = 1000
    all_rows = []
    offset = 0
    while True:
        resp = sb.table("jobs").select("company").range(offset, offset + PAGE_SIZE - 1).execute()
        all_rows.extend(resp.data)
        if len(resp.data) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return all_rows


@app.get("/api/companies/counts")
async def company_counts():
    sb = get_supabase()
    if sb:
        all_rows = _fetch_all_companies(sb)
        counts = Counter(j["company"] for j in all_rows)
        result = [{"company": c, "count": n} for c, n in sorted(counts.items(), key=lambda x: -x[1])]
        return {"companies": result}
    companies = get_local_db()[1]()
    return {"companies": [{"company": c, "count": 0} for c in companies]}


@app.get("/api/runs")
async def runs_endpoint(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    from app.db.local_db import get_runs, init_scrape_runs
    init_scrape_runs()
    runs, total = get_runs(limit=limit, offset=offset)
    return {"runs": runs, "total": total}


@app.get("/api/runs/dates")
async def run_dates():
    from app.db.local_db import get_run_dates, init_scrape_runs
    init_scrape_runs()
    return {"dates": get_run_dates()}


@app.get("/api/runs/{run_id}")
async def run_detail(run_id: int, limit: int = Query(500, ge=1, le=2000), offset: int = Query(0, ge=0)):
    from app.db.local_db import get_run_jobs, get_runs, init_scrape_runs
    init_scrape_runs()
    runs, _ = get_runs(limit=100, offset=0)
    run_info = next((r for r in runs if r["id"] == run_id), None)
    if not run_info:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "Run not found"}, status_code=404)
    jobs, total = get_run_jobs(run_id, limit=limit, offset=offset)
    return {"run": run_info, "jobs": jobs, "total": total}


@app.get("/api/runs/date/{run_date}")
async def run_by_date(run_date: str, limit: int = Query(500, ge=1, le=2000), offset: int = Query(0, ge=0)):
    from app.db.local_db import get_jobs_by_run_date, get_run_dates, init_scrape_runs
    init_scrape_runs()
    jobs, total = get_jobs_by_run_date(run_date, limit=limit, offset=offset)
    dates = get_run_dates()
    date_info = next((d for d in dates if d["run_date"] == run_date), {})
    return {"date": run_date, "jobs": jobs or [], "total": total, "summary": date_info}


@app.get("/api/jobs/applied")
async def get_applied():
    from app.db.local_db import get_applied_keys
    return {"applied": get_applied_keys()}


@app.api_route("/api/jobs/toggle-applied", methods=["GET", "POST"])
async def toggle_applied(job_key: str = Query(None)):
    from app.db.local_db import toggle_applied_job, init_applied_jobs
    init_applied_jobs()
    if not job_key:
        return {"applied": False, "applied_at": None}
    now_applied, applied_at = toggle_applied_job(job_key)
    return {"applied": now_applied, "applied_at": applied_at}


@app.get("/api/companies")
async def companies_endpoint():
    sb = get_supabase()
    if sb:
        all_rows = _fetch_all_companies(sb)
        companies = sorted(set(j["company"] for j in all_rows))
        return {"companies": companies}

    return {"companies": get_local_db()[1]()}
