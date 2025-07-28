from app.db.db_client import SupabaseDB
from app.models.job import Job
from app.emailer.emailer import Emailer

api_keys = {
    "jayeshastha@gmail.com": "re_SdxTU2JC_FnTrXWRL4B1v5gaCEGtv9ebj"
}



def fetch_top_jobs():
    db = SupabaseDB()
    client = db.get_client()
    response = client.table("jobs").select("*").limit(10).execute()
    jobs_data = response.data
    jobs = []
    for item in jobs_data:
        job = Job(
            title=item.get("title", ""),
            jobid=item.get("jobid", ""),
            company=item.get("company", ""),
            location=item.get("location", ""),
            url=item.get("url", ""),
            posted_date=item.get("posted_date", "")
        )
        jobs.append(job)
    return jobs


if __name__ == "__main__":
    jobs = fetch_top_jobs()
    print(f"Fetched {len(jobs)} jobs from database")

    sender_objects = []  

    # Create all emailer objects and store in array
    for email, api_key in api_keys.items():
        print(f"Creating emailer object for {email}...")
        try:
            emailer = Emailer(api_key=api_key, recipient_email=email)
            sender_objects.append(emailer)
            print(f"✅ Created emailer for {email}")
        except Exception as e:
            print(f"❌ Error creating emailer for {email}: {e}")

    print(f"\nCreated {len(sender_objects)} emailer objects")

    # Now access each object from array and call the function
    for i, sender in enumerate(sender_objects):
        try:
            print(
                f"\nProcessing sender {i+1}/{len(sender_objects)}: {sender.recipient_email}")

            if jobs:
                # Access the object and call the method
                result = sender.send_jobs(jobs)
                print(
                    f"✅ Successfully sent {len(jobs)} jobs to {sender.recipient_email}")
            else:
                print(f"⚠️ No jobs found for {sender.recipient_email}")

        except Exception as e:
            print(f"❌ Error sending jobs to {sender.recipient_email}: {e}")

    print(f"\nCompleted processing {len(sender_objects)} senders")
