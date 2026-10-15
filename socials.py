import os
import smtplib
from email.message import EmailMessage

try: 
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SOCIALS = [
    {"name": "GitHub",    "key": "github",    "url": "https://github.com/sarahgruy"},
    {"name": "Instagram", "key": "instagram", "url": "https://www.instagram.com/szsrahh"},
    {"name": "Discord",   "key": "discord",   "url": "https://discord.com/users/769065309490774030"},
    {"name": "LinkedIn",  "key": "linkedin",  "url": "https://linkedin.com/in/sarah-grace-gruy-b1aa14438"},
]
CONTACT_EMAIL = "sarahgruy@gmail.com"


def send_to_gmail(first, last, sender_email, message):
    """Send the visitor's message to your Gmail using Gmail's SMTP server."""
    gmail_address = os.environ.get("GMAIL_ADDRESS", CONTACT_EMAIL)
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    if not app_password:
        raise RuntimeError("GMAIL_APP_PASSWORD is not set")
    
    msg = EmailMessage()
    msg["Subject"] = f"New message from {first} {last} (personal website)"
    msg["From"] = gmail_address
    msg["To"] = gmail_address
    msg["Reply-To"] = sender_email         
    msg.set_content(
        f"Name: {first} {last}\n"
        f"Email: {sender_email}\n\n"
        f"Message:\n{message}\n"
    )
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
        server.login(gmail_address, app_password)
        server.send_message(msg)