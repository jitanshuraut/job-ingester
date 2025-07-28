from app.scrapers.A_Company.Adobe import AdobeScraper

if __name__ == "__main__":
    listener = AdobeScraper()
    jobs = listener.fetch_jobs()
    print(len(jobs))
    for job in jobs:
        print(job)