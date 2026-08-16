"""
Email Module: Sends emails securely via SMTP with validation and error handling.
"""

import os
import re
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


class EmailService:
    """Service to handle secure sending of emails."""

    EMAIL_REGEX = r"^[\w\.\+-]+@[\w\.-]+\.\w+$"

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        email_user: Optional[str] = None,
        email_pass: Optional[str] = None
    ):
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(smtp_port or os.getenv("SMTP_PORT", 587))
        self.email_user = email_user or os.getenv("EMAIL_USER")
        self.email_pass = email_pass or os.getenv("EMAIL_PASS")

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format using regex."""
        if not email:
            return False
        return bool(re.match(cls.EMAIL_REGEX, email.strip()))

    @classmethod
    def clean_spoken_email(cls, spoken_text: str) -> str:
        """
        Helper to normalize spoken email addresses (e.g., 'john at gmail dot com' -> 'john@gmail.com').
        """
        text = spoken_text.lower().strip()
        text = text.replace(" at the rate ", "@").replace(" at ", "@")
        text = text.replace(" dot ", ".").replace(" point ", ".")
        text = text.replace(" ", "")
        return text

    def send_email(self, recipient: str, subject: str, message_body: str) -> Tuple[bool, str]:
        """
        Send email to recipient. Returns (success: bool, status_message: str).
        """
        recipient = self.clean_spoken_email(recipient)

        if not self.validate_email(recipient):
            return False, f"'{recipient}' is not a valid email address."

        if not self.email_user or not self.email_pass or self.email_user == "your_email@gmail.com":
            return (
                False,
                "Email credentials are not configured. Please set EMAIL_USER and EMAIL_PASS in the .env file."
            )

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_user
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(message_body, "plain"))

            logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)

            logger.info(f"Email successfully sent to {recipient}")
            return True, f"The email to {recipient} has been sent successfully."

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP Authentication failed.")
            return False, "Failed to authenticate with the email server. Please verify your email and app password."
        except (smtplib.SMTPException, OSError) as e:
            logger.error(f"SMTP error while sending email: {e}")
            return False, f"An error occurred while sending the email: {e}"
