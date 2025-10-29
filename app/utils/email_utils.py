import smtplib
from email.mime.text import MIMEText
from fastapi import BackgroundTasks
from app.core.config import settings

def send_email(to_email: str, subject: str, body: str):
    """Send plain text email via SMTP"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SENDER_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        server.send_message(msg)


def send_verification_email(background_tasks: BackgroundTasks, to_email: str, token: str):
    """Compose and schedule sending of verification email"""
    verify_link = f"http://localhost:8000/auth/verify?token={token}"
    subject = "Confirm your email address"
    body = f"""
    Hi there!

    Please confirm your email by clicking the link below:

    {verify_link}

    This link will expire in {settings.EMAIL_TOKEN_EXPIRE_MINUTES} minutes.

    Thank you!
    """
    background_tasks.add_task(send_email, to_email, subject, body)
