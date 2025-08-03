from app.scrapers.V_Company.Visa import VisaScraper

if __name__ == "__main__":
    listener = VisaScraper()
    jobs = listener.fetch_jobs()
    print(jobs)