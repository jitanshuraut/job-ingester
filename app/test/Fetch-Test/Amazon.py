from app.scrapers.A_Company.Amazon import AmazonScraper

if __name__ == "__main__":
    listener = AmazonScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)