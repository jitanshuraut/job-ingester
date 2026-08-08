import sqlite3
import json
import logging
from app.analyzer.categorizer import categorize, get_example_urls, normalize_workday_url
from app.analyzer.fetcher import fetch_description_text
from app.analyzer.extractor import analyze_job_description

logger = logging.getLogger(__name__)


def load_jobs_from_db(company: str = None, limit: int = None) -> list[dict]:
    conn = sqlite3.connect("data/jobs.db")
    conn.row_factory = sqlite3.Row
    query = "SELECT id, title, company, location, url, posted_date FROM jobs WHERE url IS NOT NULL AND url != ''"
    params = []
    if company:
        query += " AND company = ?"
        params.append(company)
    query += " ORDER BY posted_date DESC"
    if limit:
        query += f" LIMIT {limit}"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def analyze_jobs(company: str = None, limit: int = None, save: bool = False) -> list[dict]:
    jobs = load_jobs_from_db(company, limit)
    results = []
    for job in jobs:
        url = job.get("url", "")
        platform = categorize(url)
        desc_text = fetch_description_text(url)
        analysis = analyze_job_description(desc_text) if desc_text else {"experience_years": [], "skills": [], "degrees": [], "text_length": 0}
        result = {
            "id": job["id"],
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "platform": platform,
            "experience_years": analysis["experience_years"],
            "skills": analysis["skills"],
            "degrees": analysis["degrees"],
            "text_length": analysis["text_length"],
        }
        results.append(result)
        company_pad = (job["company"] or "")[:20].ljust(20)
        title_pad = (job["title"] or "")[:50].ljust(50)
        print(f"[{platform:20s}] {company_pad} | {title_pad} | exp={analysis['experience_years']} | skills={len(analysis['skills'])}")
    if save:
        _save_results(results)
    return results


def _save_results(results: list[dict]):
    conn = sqlite3.connect("data/jobs.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_analysis (
            job_id INTEGER PRIMARY KEY,
            platform TEXT,
            experience_years TEXT,
            skills TEXT,
            degrees TEXT,
            text_length INTEGER,
            analyzed_at TEXT
        )
    """)
    from datetime import datetime
    now = datetime.now().isoformat()
    for r in results:
        conn.execute("""
            INSERT OR REPLACE INTO job_analysis (job_id, platform, experience_years, skills, degrees, text_length, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            r["id"], r["platform"],
            json.dumps(r["experience_years"]),
            json.dumps(r["skills"]),
            json.dumps(r["degrees"]),
            r["text_length"], now,
        ))
    conn.commit()
    conn.close()
    logger.info(f"Saved {len(results)} analysis results to DB")
