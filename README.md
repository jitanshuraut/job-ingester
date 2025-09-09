# Job Notifier

A Python-based job notification system that aggregates job postings from multiple sources and sends email notifications to a list of recipients.

## Features
- Aggregates jobs from various company sources using custom scrapers
- Sends job notifications via Gmail SMTP to multiple recipients
- HTML and plain-text email templates for job listings
- Environment variable support for credentials
- Modular design for easy extension

## Setup

### Prerequisites
- Python 3.8+
- Gmail account with App Password enabled
- [pip](https://pip.pypa.io/en/stable/)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/job-ingester.git
   cd job-ingester
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory:
   ```env
   GMAIL_EMAIL=your_gmail_address@gmail.com
   GMAIL_APP_PASSWORD=your_app_password
   ```

## Usage

### Run the Notifier
Edit `main.py` to set your recipient emails:
```python
emails = [
    "recipient1@example.com",
    "recipient2@example.com",
]
```
Run the main script:
```sh
python main.py
```

### Test Email
You can send a test email using:
```python
emailer = Emailer(recipient_emails=emails)
result = emailer.send_test_email()
print(result)
```

## Project Structure
```
job-ingester/
├── app/
│   ├── core/
│   ├── db/
│   ├── emailer/
│   ├── models/
│   ├── scrapers/
│   └── utils/
├── main.py
├── requirements.txt
├── README.md
└── .env
```

## Extending
- Add new scrapers in `app/scrapers/`
- Update `JobAggregator` logic in `app/core/Aggregator.py`
- Customize email templates in `app/emailer/emailer.py`

## Troubleshooting
- Ensure your Gmail App Password is correct
- Check your `.env` file for correct credentials
- Review logs for error messages

## License
MIT

## Author
- [Your Name](https://github.com/yourusername)
