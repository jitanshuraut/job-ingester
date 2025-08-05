from dataclasses import dataclass
@dataclass
class EmailConfig:
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    app_password: str = ""
    sender_name: str = "Job Notifier"
    use_tls: bool = True
    timeout: int = 30