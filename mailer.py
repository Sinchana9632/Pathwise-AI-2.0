import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import streamlit as st

def send_email_async(to_email, subject, body_text):
    """
    Spawns a background thread to send an email so the Streamlit UI doesn't freeze.
    """
    thread = threading.Thread(target=execute_email_send, args=(to_email, subject, body_text))
    thread.start()

def execute_email_send(to_email, subject, body_text):
    """
    Handles the actual SMTP connection logic safely in the background.
    """
    # 📝 Configuration: Replace these with your actual SMTP provider details
    # For Gmail: You will need to generate an "App Password" from your Google Account settings.
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "your-professional-email@gmail.com"  
    SENDER_PASSWORD = "your-app-password-here"          

    # Check if placeholders haven't been configured yet
    if SENDER_EMAIL == "your-professional-email@gmail.com":
        print("[Mailer] SMTP credentials not configured. Skipping email delivery.")
        return

    try:
        # Construct the email packet
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'plain'))

        # Establish connection and dispatch
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Upgrade connection to secure TLS
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[Mailer] Successfully dispatched email notification to {to_email}")
    except Exception as e:
        print(f"[Mailer] Failed to send email due to error: {e}")