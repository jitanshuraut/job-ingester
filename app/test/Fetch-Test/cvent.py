from app.scrapers.C_Company.cvent import CventScraper

if __name__ == "__main__":
    listener = CventScraper()
    jobs = listener.fetch_jobs()
    print(jobs)