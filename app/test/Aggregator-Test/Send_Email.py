from app.db.db_client import SupabaseDB
from app.models.job import Job
from app.emailer.emailer import Emailer


# Example usage
def main():
    """Example usage of the Gmail Job Emailer"""

    # Primary usage - from environment variables
    emailer = Emailer(recipient_emails=[
                      "jayeshastha@gmail.com", "ui21cs27@iiitsurat.ac.in"])

    # Test the emailer
    result = emailer.send_test_email()
    print("Test email result:", result)

    # Example with actual jobs (assuming you have Job objects)
    # jobs = [...]  # Your list of Job objects
    # result = emailer.send_jobs(jobs)
    # print("Job email result:", result)


if __name__ == "__main__":
    main()
