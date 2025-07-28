from app.scrapers.C_Company.Cadence import CadenceScraper

if __name__ == "__main__":
    listener = CadenceScraper()
    jobs = listener.fetch_jobs()
    print(jobs)