from app.scrapers.A_Company.Analog_Devices import AnalogDevicesScraper

if __name__ == "__main__":
    listener = AnalogDevicesScraper()
    jobs = listener.fetch_jobs()
    for job in jobs:
        print(job)