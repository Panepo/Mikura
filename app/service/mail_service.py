import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SMTP configuration from .env
SMTP_SERVER = os.getenv('MISSMTP_SERVER', '')
SMTP_PORT = int(os.getenv('MISSMTP_PORT', 0))
MAIL_FROM = os.getenv('MAIL_FROM', 'mikura-no-reply@srdd.getac.com.tw')
# Note: You may need to add MAIL_PASSWORD to your .env file if authentication is required


def send_email(recipient: str, subject: str, body: str, html_body: str = None):
    """
    Send an email using SMTP configuration from .env

    Args:
        recipient: Email address of the recipient
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML email body
    """
    # Create message
    if html_body:
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText(body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
    else:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, 'plain'))

    msg['From'] = MAIL_FROM
    msg['To'] = recipient
    msg['Subject'] = subject

    try:
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection

            # If authentication is required, uncomment the following line:
            # server.login(MAIL_FROM, os.getenv('MAIL_PASSWORD'))

            server.send_message(msg)
            print(f"Email sent successfully to {recipient}")

    except Exception as e:
        print(f"Failed to send email to {recipient}: {str(e)}")
        raise


def send_welcome_email(recipient: str, username: str):
    """
    Send a welcome email to a new user

    Args:
        recipient: Email address of the recipient
        username: User's name
    """
    subject = "Welcome to Mikura!"
    body = f"Dear {username},\n\nWelcome to Mikura! We're excited to have you on board.\n\nBest regards,\nThe Mikura Team"

    html_body = f"""
    <html>
        <body>
            <h2>Welcome to Mikura, {username}!</h2>
            <p>We're excited to have you on board.</p>
            <p>Best regards,<br>The Mikura Team</p>
        </body>
    </html>
    """

    send_email(recipient, subject, body, html_body)


if __name__ == "__main__":
    # Test email sending (uncomment to test)
    # send_email(
    #     recipient="test@example.com",
    #     subject="Test Email",
    #     body="This is a test email sent from Mikura.",
    #     html_body="<h1>This is a test email</h1><p>Sent from Mikura.</p>"
    # )
    pass
