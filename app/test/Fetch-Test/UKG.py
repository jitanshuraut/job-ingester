from app.scrapers.U_Company.UKG import UKGScraper

if __name__ == "__main__":
    listener = UKGScraper()
    jobs = listener.fetch_jobs()
    print(jobs)