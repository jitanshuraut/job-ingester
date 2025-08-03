from app.scrapers.T_Company.Target import TargetScraper

if __name__ == "__main__":
    listener = TargetScraper()
    jobs = listener.fetch_jobs()
    print(jobs)