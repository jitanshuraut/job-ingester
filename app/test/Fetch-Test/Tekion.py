from app.scrapers.T_Company.Tekion import TekionScraper

if __name__ == "__main__":
    listener = TekionScraper()
    jobs = listener.fetch_jobs()
    print(jobs)