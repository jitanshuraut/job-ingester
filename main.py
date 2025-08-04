import os
from dotenv import load_dotenv
import psutil
from app.core.Aggregator import JobAggregator
from app.emailer.emailer import Emailer

load_dotenv()

api_keys = {
    "jayeshastha@gmail.com": os.environ.get("API_KEY_JAYESHASTHA"),
    "jayeshastha@gmail.com": os.environ.get("API_KEY_JAYESHASTHA2"),
    "manassoni575@gmail.com": os.environ.get("API_KEY_MANASSONI"),

}


def main():
    print("=== Job Notifier Cron Started ===")
    process = psutil.Process()
    print(
        f"Memory usage at start: {process.memory_info().rss / 1024 ** 2:.2f} MB")

    aggregator = JobAggregator()
    new_jobs = aggregator.run()
    sender_objects = []

    for email, api_key in api_keys.items():
        print(f"Creating emailer object for {email}...")
        try:
            emailer = Emailer(api_key=api_key, recipient_email=email)
            sender_objects.append(emailer)
            print(f"✅ Created emailer for {email}")
        except Exception as e:
            print(f"❌ Error creating emailer for {email}: {e}")

    print(f"\nCreated {len(sender_objects)} emailer objects")

    for i, sender in enumerate(sender_objects):
        try:
            print(
                f"\nProcessing sender {i+1}/{len(sender_objects)}: {sender.recipient_email}")

            if new_jobs:
                sender.send_jobs(new_jobs)
                print(
                    f"✅ Successfully sent {len(new_jobs)} jobs to {sender.recipient_email}")
            else:
                print(f"⚠️ No jobs found for {sender.recipient_email}")

        except Exception as e:
            print(f"❌ Error sending jobs to {sender.recipient_email}: {e}")

    print(f"\nCompleted processing {len(sender_objects)} senders")
    print(
        f"Memory usage at end: {process.memory_info().rss / 1024 ** 2:.2f} MB")
    print("=== Job Notifier Cron Finished ===")


if __name__ == "__main__":
    main()
