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


def send_email(new_jobs):
    try:
        emailer = Emailer(recipient_emails=emails)
        print(f"✅ Created emailer for recipients: {emails}")
        if new_jobs:
            result = emailer.send_jobs(new_jobs)
            if result.get("status") == "success":
                print(f"✅ Emailed {len(new_jobs)} jobs to {emails}")
            else:
                print(f"❌ Email failed: {result.get('message')}")
        else:
            print(f"⚠️ No jobs to email")
    except Exception as e:
        print(f"❌ Email error: {e}")


def send_telegram(new_jobs):
    try:
        from app.telegram.telegram_bot import TelegramBot
        bot = TelegramBot()
        result = bot.send_jobs(new_jobs)
        if result.get("ok"):
            print(f"✅ Telegram sent {len(new_jobs)} jobs")
        else:
            print(f"❌ Telegram failed: {result.get('error', 'unknown')}")
    except Exception as e:
        print(f"ℹ️ Telegram not configured: {e}")


def main():
    print("=== Job Notifier Cron Started ===")
    process = psutil.Process()
    print(
        f"Memory usage at start: {process.memory_info().rss / 1024 ** 2:.2f} MB")

    aggregator = JobAggregator()
    new_jobs = aggregator.run()

    send_email(new_jobs)
    send_telegram(new_jobs)

    print(
        f"Memory usage at end: {process.memory_info().rss / 1024 ** 2:.2f} MB")
    print("=== Job Notifier Cron Finished ===")


if __name__ == "__main__":
    main()
