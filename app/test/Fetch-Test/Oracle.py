from app.scrapers.O_Company.Oracle import OracleScraper

if __name__ == "__main__":
    listener = OracleScraper()
    jobs = listener.fetch_jobs()
    print(jobs)