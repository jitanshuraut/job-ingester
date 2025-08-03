from app.scrapers.T_Company.Texas import TexasScraper

if __name__ == "__main__":
    listener = TexasScraper()
    jobs = listener.fetch_jobs()
    print(jobs)