from app.scrapers.T_Company.Thoughtworks import ThoughtworksScraper

if __name__ == "__main__":
    listener = ThoughtworksScraper()
    jobs = listener.fetch_jobs()
    print(jobs)