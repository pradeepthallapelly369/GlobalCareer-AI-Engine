import os
import sys
import smtplib
from email.mime.text import MIMEText

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config.settings import SMTP_EMAIL, SMTP_APP_PASSWORD, TARGET_EMAIL

def send_test():
    print(f"Sending test email from {SMTP_EMAIL} to {TARGET_EMAIL}")
    msg = MIMEText("This is a test email to verify SMTP delivery from GlobalCareer-AI-Engine.", "plain")
    msg["Subject"] = "Test Email Delivery"
    msg["From"] = SMTP_EMAIL
    msg["To"] = TARGET_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            smtp.send_message(msg)
        print("✅ Test email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending test email: {e}")

if __name__ == "__main__":
    send_test()
