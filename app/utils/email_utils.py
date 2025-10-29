import os
import smtplib
from email.mime.text import MIMEText
from fastapi import BackgroundTasks
from app.core.config import settings

def send_email(to_email: str, subject: str, body: str):
    """Send plain text email via SMTP or print to console if dev/testing"""
    if not settings.SMTP_SERVER or not settings.SMTP_PORT:
        print(f"[DEV EMAIL] To: {to_email}\nSubject: {subject}\n{body}")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SENDER_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            if settings.SENDER_PASSWORD:
                server.starttls()  # required for Outlook / secure SMTP
                server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"[EMAIL ERROR] Could not send email: {e}")
        # fallback: print email content for dev/testing
        print(f"[FALLBACK EMAIL] To: {to_email}\nSubject: {subject}\n{body}")

def send_verification_email(background_tasks: BackgroundTasks, to_email: str, token: str):
    """Compose and schedule sending of verification email"""
    verify_link = f"http://localhost:8000/users/verify?token={token}"
    subject = "Confirm your email address"
    body = f"""
Hi there!

Please confirm your email by clicking the link below:

{verify_link}

This link will expire in {settings.EMAIL_TOKEN_EXPIRE_MINUTES} minutes.

Thank you!
"""
    background_tasks.add_task(send_email, to_email, subject, body)
