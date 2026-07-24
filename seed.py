import sqlite3, os

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "jobs.db")

os.makedirs(DB_DIR, exist_ok=True)
conn = sqlite3.connect(DB_PATH)
conn.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        jobid TEXT,
        company TEXT NOT NULL,
        location TEXT,
        url TEXT,
        posted_date TEXT
    )
""")

jobs = [
    ("Software Engineer", "REQ-001", "Google", "Bangalore, India", "https://careers.google.com/jobs/1", "2026-07-18 10:00:00"),
    ("Senior SDE", "REQ-002", "Amazon", "Hyderabad, India", "https://amazon.jobs/2", "2026-07-17 09:30:00"),
    ("Frontend Developer", "REQ-003", "Adobe", "Noida, India", "https://adobe.careers/3", "2026-07-16 14:00:00"),
    ("Data Scientist", "REQ-004", "Microsoft", "Bangalore, India", "https://careers.microsoft.com/4", "2026-07-15 11:00:00"),
    ("DevOps Engineer", "REQ-005", "Uber", "Bangalore, India", "https://uber.careers/5", "2026-07-14 16:00:00"),
    ("Backend Engineer", "REQ-006", "Sprinklr", "Gurgaon, India", "https://sprinklr.com/careers/6", "2026-07-13 08:00:00"),
    ("ML Engineer", "REQ-007", "Goldman Sachs", "Bangalore, India", "https://goldmansachs.com/careers/7", "2026-07-12 12:00:00"),
    ("Product Manager", "REQ-008", "JPMorgan", "Mumbai, India", "https://jpmorgan.com/careers/8", "2026-07-11 15:00:00"),
    ("Full Stack Developer", "REQ-009", "Visa", "Bangalore, India", "https://visa.com/careers/9", "2026-07-10 10:00:00"),
    ("QA Engineer", "REQ-010", "CrowdStrike", "Pune, India", "https://crowdstrike.com/careers/10", "2026-07-09 09:00:00"),
]

conn.executemany(
    "INSERT INTO jobs (title, jobid, company, location, url, posted_date) VALUES (?, ?, ?, ?, ?, ?)",
    jobs,
)
conn.commit()
print(f"Seeded {len(jobs)} jobs into {DB_PATH}")
conn.close()
