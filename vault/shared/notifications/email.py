import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


class EmailClient:
    """SMTP email client. Reads config from environment variables.

    Required env vars:
        SMTP_HOST
        SMTP_PORT         (default: 587)
        SMTP_USER
        SMTP_PASSWORD
        NOTIFICATION_EMAIL
    """

    def __init__(self):
        self._host = os.getenv("SMTP_HOST", "")
        self._port = int(os.getenv("SMTP_PORT", "587"))
        self._user = os.getenv("SMTP_USER", "")
        self._password = os.getenv("SMTP_PASSWORD", "")
        self._to = os.getenv("NOTIFICATION_EMAIL", "")

    def send(self, subject: str, body_text: str) -> None:
        """Send a plain-text email to NOTIFICATION_EMAIL.

        Raises:
            ValueError: if any required env var is missing.
            smtplib.SMTPException: on delivery failure.
        """
        missing = [
            k
            for k, v in {
                "SMTP_HOST": self._host,
                "SMTP_USER": self._user,
                "SMTP_PASSWORD": self._password,
                "NOTIFICATION_EMAIL": self._to,
            }.items()
            if not v
        ]
        if missing:
            raise ValueError(f"Missing email env vars: {', '.join(missing)}")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._user
        msg["To"] = self._to
        msg.attach(MIMEText(body_text, "plain"))

        with smtplib.SMTP(self._host, self._port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self._user, self._password)
            smtp.sendmail(self._user, self._to, msg.as_string())
