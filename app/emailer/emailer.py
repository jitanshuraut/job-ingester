import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.job import Job
from dotenv import load_dotenv
from typing import List, Optional
from collections import defaultdict
from jinja2 import Template
from uuid import uuid4
from dataclasses import dataclass
from datetime import datetime
from app.models.email import EmailConfig


class EmailException(Exception):
    """Custom exception for email operations"""
    pass


class Emailer:
    def __init__(self, recipient_emails: list[str], sender_name: str = "Job Notifier"):
        load_dotenv()
        sender_email = os.getenv("GMAIL_EMAIL")
        app_password = os.getenv("GMAIL_APP_PASSWORD")
        if not sender_email or not app_password:
            raise EmailException(
                "GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables are required"
            )
        self.config = EmailConfig(
            sender_email=sender_email,
            app_password=app_password,
            sender_name=sender_name
        )
        self.recipient_emails = recipient_emails
        self.logger = self._setup_logger()
        self._validate_config()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the emailer"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _validate_config(self) -> None:
        """Validate email configuration"""
        if not self.config.sender_email:
            raise EmailException("Sender email is required")
        if not self.config.app_password:
            raise EmailException("App password is required")
        if not self.recipient_emails or not isinstance(self.recipient_emails, list):
            raise EmailException(
                "Recipient emails are required and must be a list")
        for email in self.recipient_emails:
            if "@" not in email:
                raise EmailException(f"Invalid email format: {email}")

    def _create_job_email_template(self) -> str:
        """Create the HTML email template for job notifications"""
        return """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; background: #f8f9fa; padding: 24px;">
            <div style="max-width: 700px; margin: auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 24px;">
                <h2 style="color: #007bff; margin-bottom: 24px;">🚀 New Jobs Available</h2>
                {% if company_jobs %}
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
                {% else %}
                    <div style="padding: 20px; text-align: center; color: #6c757d;">
                        <p>No new jobs found at this time.</p>
                        <p>We'll continue monitoring and notify you when new opportunities become available.</p>
                    </div>
                {% endif %}
                <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #dee2e6; font-size: 13px; color: #6c757d;">
                    <p>This is an automated notification from Job Notifier.</p>
                    <p>Notification ID: {{ notification_id }}</p>
                    <p>Generated on: {{ timestamp }}</p>
                </div>
            </div>
        </div>
        """

    def _create_message(self, subject: str, html_content: str, text_content: Optional[str] = None) -> MIMEMultipart:
        """Create MIME message for email"""
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{self.config.sender_name} <{self.config.sender_email}>"
        msg['To'] = ", ".join(self.recipient_emails)
        msg['Subject'] = subject
        msg['X-Entity-Ref-ID'] = str(uuid4())
        # Add text version if provided
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
        # Add HTML version
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        return msg

    def _generate_text_content(self, jobs: List[Job]) -> str:
        """Generate plain text version of job email"""
        if not jobs:
            return "No new jobs found at this time. We'll continue monitoring and notify you when new opportunities become available."

        company_jobs = defaultdict(list)
        for job in jobs:
            company_jobs[job.company].append(job)

        text_content = "🚀 New Jobs Available\n\n"

        for company, company_job_list in company_jobs.items():
            text_content += f"{company}\n" + "=" * len(company) + "\n\n"

            for job in company_job_list:
                text_content += f"• {job.title}\n"
                text_content += f"  Location: {job.location}\n"
                text_content += f"  Posted: {job.posted_date}\n"
                text_content += f"  URL: {job.url}\n\n"

            text_content += "\n"

        text_content += "This is an automated notification from Job Notifier."
        return text_content

    def send_jobs(self, jobs: List[Job]) -> dict:
        try:
            # Organize jobs by company
            company_jobs = defaultdict(list)
            for job in jobs:
                company_jobs[job.company].append(job)

            # Create HTML content using template
            template_str = self._create_job_email_template()
            template = Template(template_str)
            html_content = template.render(
                company_jobs=company_jobs,
                notification_id=str(uuid4()),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            # Generate text content
            text_content = self._generate_text_content(jobs)

            # Determine subject
            job_count = len(jobs)
            if job_count == 0:
                subject = "Job Notifier - No New Jobs"
            elif job_count == 1:
                subject = f"Job Notifier - 1 New Job Available"
            else:
                subject = f"Job Notifier - {job_count} New Jobs Available"

            # Create message
            message = self._create_message(subject, html_content, text_content)

            # Send email
            return self._send_email(message, subject, job_count)

        except Exception as e:
            error_msg = f"Error preparing email: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'timestamp': datetime.now().isoformat()
            }

    def _send_email(self, message: MIMEMultipart, subject: str, job_count: int) -> dict:
        """Send the email via Gmail SMTP"""
        try:
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port,
                              timeout=self.config.timeout) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.sender_email,
                             self.config.app_password)
                # Send email to all recipients
                result = server.send_message(
                    message, to_addrs=self.recipient_emails)
                success_msg = f"Job notification sent successfully! ({job_count} jobs)"
                self.logger.info(success_msg)
                return {
                    'status': 'success',
                    'message': success_msg,
                    'job_count': job_count,
                    'recipient': self.recipient_emails,
                    'timestamp': datetime.now().isoformat(),
                    'message_id': message.get('X-Entity-Ref-ID')
                }
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "Authentication failed. Check email and app password."
            self.logger.error(f"{error_msg} Details: {str(e)}")
            return {
                'status': 'error',
                'message': error_msg,
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Recipient(s) {self.recipient_emails} were refused by server"
            self.logger.error(f"{error_msg} Details: {str(e)}")
            return {
                'status': 'error',
                'message': error_msg,
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = f"Error sending email via Gmail SMTP: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def send_test_email(self) -> dict:
        """Send a test email to verify configuration"""
        test_job = type('TestJob', (), {
            'title': 'Test Job Position',
            'company': 'Test Company',
            'location': 'Test Location',
            'posted_date': datetime.now().strftime("%Y-%m-%d"),
            'url': 'https://example.com/test-job'
        })()

        return self.send_jobs([test_job])
