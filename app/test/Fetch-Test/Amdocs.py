from app.scrapers.A_Company.Amdocs import AmdocsScraper

if __name__ == "__main__":
    listener = AmdocsScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)