import os
from dotenv import load_dotenv
import psutil
from app.core.Aggregator import JobAggregator
from app.emailer.emailer import Emailer

load_dotenv()


emails = [
    "jayeshastha@gmail.com",
    "manassoni575@gmail.com",
    "gbhardwaj572@gmail.com"
]


def main():
    print("=== Job Notifier Cron Started ===")
    process = psutil.Process()
    print(
        f"Memory usage at start: {process.memory_info().rss / 1024 ** 2:.2f} MB")

    aggregator = JobAggregator()
    new_jobs = aggregator.run()
    print(f"Creating emailer object for all recipients...")
    try:
        emailer = Emailer(recipient_emails=emails)
        print(f"✅ Created emailer for recipients: {emails}")
    except Exception as e:
        print(f"❌ Error creating emailer: {e}")
        return

    if new_jobs:
        try:
            emailer.send_jobs(new_jobs)
            print(f"✅ Successfully sent {len(new_jobs)} jobs to {emails}")
        except Exception as e:
            print(f"❌ Error sending jobs to {emails}: {e}")
    else:
        print(f"⚠️ No jobs found for {emails}")
    print(
        f"Memory usage at end: {process.memory_info().rss / 1024 ** 2:.2f} MB")
    print("=== Job Notifier Cron Finished ===")


if __name__ == "__main__":
    main()
