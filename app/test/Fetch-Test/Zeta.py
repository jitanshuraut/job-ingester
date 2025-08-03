from app.scrapers.Z_Company.Zeta import ZetaScraper

if __name__ == "__main__":
    listener = ZetaScraper()
    jobs = listener.fetch_jobs()
    print(jobs)