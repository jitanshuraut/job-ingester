from app.scrapers.Q_Company.Quantiphi import QuantiphiScraper

if __name__ == "__main__":
    listener = QuantiphiScraper()
    jobs = listener.fetch_jobs()
    print(jobs)