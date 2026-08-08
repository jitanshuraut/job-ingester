import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "jobs.db")


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            jobid TEXT,
            company TEXT NOT NULL,
            location TEXT,
            url TEXT UNIQUE,
            posted_date TEXT,
            experience_years TEXT DEFAULT '',
            skills TEXT DEFAULT ''
        )
    """)
    for col in ("experience_years", "skills"):
        try:
            conn.execute(f"ALTER TABLE jobs ADD COLUMN {col} TEXT DEFAULT ''")
        except Exception:
            pass
    conn.execute("CREATE INDEX IF NOT EXISTS idx_company ON jobs(company)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_url ON jobs(url)")
    conn.commit()
    conn.close()


def sync_from_supabase(supabase_client):
    init_db()
    conn = get_connection()
    offset = 0
    batch_size = 1000
    total = 0
    while True:
        resp = supabase_client.table("jobs").select("url, jobid, title, company, location, posted_date").range(offset, offset + batch_size - 1).execute()
        rows = resp.data
        if not rows:
            break
        for row in rows:
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO jobs (title, jobid, company, location, url, posted_date, experience_years, skills)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (row.get("title", ""), row.get("jobid", ""), row.get("company", ""),
                     row.get("location", ""), row.get("url", ""), row.get("posted_date", ""),
                     row.get("experience_years") or "", row.get("skills") or ""),
                )
            except Exception:
                pass
        total += len(rows)
        if len(rows) < batch_size:
            break
        offset += batch_size
    conn.commit()
    conn.close()
    return total


def job_exists_by_url(url: str) -> bool:
    if not url:
        return False
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM jobs WHERE url = ? LIMIT 1", (url,)).fetchone()
    conn.close()
    return row is not None


def job_exists_by_jobid(jobid: str) -> bool:
    if not jobid:
        return False
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM jobs WHERE jobid = ? LIMIT 1", (jobid,)).fetchone()
    conn.close()
    return row is not None


def job_exists(job: "Job") -> bool:
    if job.url and job_exists_by_url(job.url):
        return True
    if job.jobid and job_exists_by_jobid(job.jobid):
        return True
    return False


def get_jobs(company=None, search=None, start_date=None, end_date=None, limit=100, offset=0):
    conn = get_connection()
    query = "SELECT * FROM jobs"
    params = []
    conditions = []

    if company:
        conditions.append("jobs.company = ?")
        params.append(company)
    if search:
        conditions.append("(jobs.title LIKE ? OR jobs.company LIKE ? OR jobs.location LIKE ?)")
        like = f"%{search}%"
        params.extend([like, like, like])
    if start_date:
        conditions.append("jobs.posted_date >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("jobs.posted_date <= ?")
        params.append(end_date)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY jobs.posted_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()

    count_query = "SELECT COUNT(*) as total FROM jobs"
    count_params = []
    count_conditions = []
    if company:
        count_conditions.append("company = ?")
        count_params.append(company)
    if search:
        count_conditions.append("(title LIKE ? OR company LIKE ? OR location LIKE ?)")
        like = f"%{search}%"
        count_params.extend([like, like, like])
    if start_date:
        count_conditions.append("posted_date >= ?")
        count_params.append(start_date)
    if end_date:
        count_conditions.append("posted_date <= ?")
        count_params.append(end_date)
    if count_conditions:
        count_query += " WHERE " + " AND ".join(count_conditions)
    total = conn.execute(count_query, count_params).fetchone()["total"]

    conn.close()
    return [dict(row) for row in rows], total


def get_companies():
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT company FROM jobs ORDER BY company"
    ).fetchall()
    conn.close()
    return [row["company"] for row in rows]


def insert_job(title, jobid, company, location, url, posted_date, experience_years="", skills=""):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO jobs (title, jobid, company, location, url, posted_date, experience_years, skills) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (title, jobid, company, location, url, posted_date, experience_years, skills),
        )
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()


def init_scrape_runs():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS scrape_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TEXT NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            total_fetched INTEGER DEFAULT 0,
            new_inserted INTEGER DEFAULT 0,
            skipped INTEGER DEFAULT 0,
            status TEXT DEFAULT 'running'
        );
        CREATE TABLE IF NOT EXISTS scrape_run_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            jobid TEXT,
            company TEXT NOT NULL,
            location TEXT,
            url TEXT,
            posted_date TEXT,
            was_new INTEGER DEFAULT 0,
            FOREIGN KEY (run_id) REFERENCES scrape_runs(id)
        );
        CREATE INDEX IF NOT EXISTS idx_run_jobs_run ON scrape_run_jobs(run_id);
        CREATE INDEX IF NOT EXISTS idx_runs_date ON scrape_runs(run_date);
    """)
    conn.commit()
    conn.close()


def create_run(started_at: str) -> int:
    run_date = started_at[:10]
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO scrape_runs (run_date, started_at, status) VALUES (?, ?, 'running')",
        (run_date, started_at),
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id


def complete_run(run_id: int, total_fetched: int, new_inserted: int, skipped: int, ended_at: str):
    conn = get_connection()
    conn.execute(
        "UPDATE scrape_runs SET ended_at = ?, total_fetched = ?, new_inserted = ?, skipped = ?, status = 'completed' WHERE id = ?",
        (ended_at, total_fetched, new_inserted, skipped, run_id),
    )
    conn.commit()
    conn.close()


def add_run_jobs(run_id: int, jobs: list, was_new: bool):
    conn = get_connection()
    w = 1 if was_new else 0
    for j in jobs:
        try:
            conn.execute(
                "INSERT INTO scrape_run_jobs (run_id, title, jobid, company, location, url, posted_date, was_new) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (run_id, j.title, j.jobid, j.company, j.location, j.url, j.posted_date, w),
            )
        except Exception:
            pass
    conn.commit()
    conn.close()


def get_runs(limit=50, offset=0):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM scrape_runs ORDER BY started_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) as c FROM scrape_runs").fetchone()["c"]
    conn.close()
    return [dict(r) for r in rows], total


def get_run_jobs(run_id: int, limit=500, offset=0):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM scrape_run_jobs WHERE run_id = ? ORDER BY was_new DESC, id ASC LIMIT ? OFFSET ?",
        (run_id, limit, offset),
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) as c FROM scrape_run_jobs WHERE run_id = ?", (run_id,)).fetchone()["c"]
    conn.close()
    return [dict(r) for r in rows], total


def get_run_dates():
    conn = get_connection()
    rows = conn.execute(
        "SELECT run_date, COUNT(*) as run_count, SUM(total_fetched) as total_jobs, SUM(new_inserted) as new_jobs FROM scrape_runs GROUP BY run_date ORDER BY run_date DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_jobs_by_run_date(run_date: str, limit=500, offset=0):
    conn = get_connection()
    rows = conn.execute(
        """SELECT j.* FROM scrape_run_jobs j
           JOIN scrape_runs r ON j.run_id = r.id
           WHERE r.run_date = ?
           ORDER BY r.started_at DESC, j.was_new DESC
           LIMIT ? OFFSET ?""",
        (run_date, limit, offset),
    ).fetchall()
    total = conn.execute(
        "SELECT COUNT(*) as c FROM scrape_run_jobs j JOIN scrape_runs r ON j.run_id = r.id WHERE r.run_date = ?",
        (run_date,),
    ).fetchone()["c"]
    conn.close()
    return [dict(r) for r in rows], total


def get_job_id(url: str) -> int | None:
    if not url:
        return None
    conn = get_connection()
    row = conn.execute("SELECT id FROM jobs WHERE url = ?", (url,)).fetchone()
    conn.close()
    return row["id"] if row else None


def save_analysis(job_id: int, data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO job_analysis
            (job_id, platform, experience_years, skills, degrees, text_length, analyzed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        data.get("platform", ""),
        data.get("experience_years", "[]"),
        data.get("skills", "[]"),
        data.get("degrees", "[]"),
        data.get("text_length", 0),
        data.get("analyzed_at", ""),
    ))
    conn.commit()
    conn.close()


def init_applied_jobs():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applied_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_key TEXT UNIQUE NOT NULL,
            applied_at TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_applied_key ON applied_jobs(job_key)")
    conn.commit()
    conn.close()


def toggle_applied_job(job_key: str) -> tuple:
    conn = get_connection()
    row = conn.execute("SELECT applied_at FROM applied_jobs WHERE job_key = ?", (job_key,)).fetchone()
    if row:
        conn.execute("DELETE FROM applied_jobs WHERE job_key = ?", (job_key,))
        conn.commit()
        conn.close()
        return (False, None)
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).isoformat()
    conn.execute("INSERT INTO applied_jobs (job_key, applied_at) VALUES (?, ?)",
                 (job_key, ts))
    conn.commit()
    conn.close()
    return (True, ts)


def get_applied_keys() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT job_key, applied_at FROM applied_jobs ORDER BY applied_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_job_applied(job_key: str) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM applied_jobs WHERE job_key = ?", (job_key,)).fetchone()
    conn.close()
    return row is not None
