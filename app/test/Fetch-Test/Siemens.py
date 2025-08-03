from app.scrapers.S_Company.Siemens import SiemensScraper

if __name__ == "__main__":
    listener = SiemensScraper()
    jobs = listener.fetch_jobs()
    print(jobs)