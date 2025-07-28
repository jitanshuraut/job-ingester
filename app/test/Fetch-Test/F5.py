from app.scrapers.F_Company.F5 import F5Scraper

if __name__ == "__main__":
    listener = F5Scraper()
    jobs = listener.fetch_jobs()
    print(jobs)