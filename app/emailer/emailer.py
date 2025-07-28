import os
import resend
from app.models.job import Job
from dotenv import load_dotenv
from typing import List, Type
from collections import defaultdict
from jinja2 import Template
from uuid import uuid4


class Emailer:
    def __init__(self, api_key: str, recipient_email: str):
        resend.api_key = api_key
        self.recipient_email = recipient_email

    def send_jobs(self, jobs: List[Job]):
        if jobs:
            company_jobs = defaultdict(list)
            for job in jobs:
                company_jobs[job.company].append(job)

            template_str = """
            <div style="font-family: 'Segoe UI', Arial, sans-serif; background: #f8f9fa; padding: 24px;">
                <div style="max-width: 700px; margin: auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 24px;">
                    <h2 style="color: #007bff; margin-bottom: 24px;">🚀 New Jobs Available</h2>
                    {% for company, jobs in company_jobs.items() %}
                        <h3 style="color: #343a40; margin-top: 32px;">{{ company }}</h3>
                        <table style="width:100%; border-collapse:collapse; margin-bottom: 16px;">
                            <thead>
                                <tr style="background: #007bff; color: #fff;">
                                    <th style="padding: 10px; border: 1px solid #dee2e6;">Title</th>
                                    <th style="padding: 10px; border: 1px solid #dee2e6;">Location</th>
                                    <th style="padding: 10px; border: 1px solid #dee2e6;">Posted Date</th>
                                    <th style="padding: 10px; border: 1px solid #dee2e6;">Link</th>
                                </tr>
                            </thead>
                            <tbody>
                            {% for job in jobs %}
                                <tr style="background: {% if loop.index0 % 2 == 0 %}#f2f6fc{% else %}#fff{% endif %};">
                                    <td style="padding: 10px; border: 1px solid #dee2e6;">{{ job.title }}</td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6;">{{ job.location }}</td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6;">{{ job.posted_date }}</td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6;">
                                        <a href="{{ job.url }}" style="color: #007bff; text-decoration: underline;" target="_blank">View</a>
                                    </td>
                                </tr>
                            {% endfor %}
                            </tbody>
                        </table>
                    {% endfor %}
                    <div style="font-size: 13px; color: #6c757d;">This is an automated notification from Job Notifier.</div>
                </div>
            </div>
            """
            template = Template(template_str)
            html_content = template.render(company_jobs=company_jobs)
        else:
            html_content = ""

        params = {
            "from": "Job Notifier <onboarding@resend.dev>",
            "to": [self.recipient_email],
            "subject": "New Jobs Notification",
            "html": html_content,
            "headers": {
                "X-Entity-Ref-ID": str(uuid4())
            }
        }

        try:
          
                email = resend.Emails.send(params)
                print(email)
        except Exception as e:
            print("Error sending email via Resend API:", e)
            print("Params used:", params)
