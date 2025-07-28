from app.scrapers.G_Company.GoldMan import GoldManScraper

if __name__ == "__main__":
    listener = GoldManScraper()
    jobs = listener.fetch_jobs()
    print(jobs)