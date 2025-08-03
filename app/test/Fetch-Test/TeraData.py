from app.scrapers.T_Company.TeraData import TeraDataScraper

if __name__ == "__main__":
    listener = TeraDataScraper()
    jobs = listener.fetch_jobs()
    print(jobs)