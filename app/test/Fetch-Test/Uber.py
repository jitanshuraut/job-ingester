from app.scrapers.U_Company.Uber import UberScraper

if __name__ == "__main__":
    listener = UberScraper()
    jobs = listener.fetch_jobs()
    print(jobs)