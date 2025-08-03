from app.scrapers.Z_Company.ZS import ZSScraper

if __name__ == "__main__":
    listener = ZSScraper()
    jobs = listener.fetch_jobs()
    print(jobs)