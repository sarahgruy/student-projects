import os
import smtplib
from email.message import EmailMessage

from flask import (Flask, render_template, request, redirect, url_for, flash)

from Lab_3 import linked_bp
from stack import stack_bp

try:  # lets you keep your secrets in a local .env file
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.register_blueprint(linked_bp)
app.register_blueprint(stack_bp)


SOCIALS = [
    {"name": "GitHub",    "key": "github",    "url": "https://github.com/sarahgruy"},
    {"name": "Instagram", "key": "instagram", "url": "https://www.instagram.com/szsrahh"},
    {"name": "Discord",   "key": "discord",   "url": "https://discord.com/users/769065309490774030"},
    {"name": "LinkedIn",  "key": "linkedin",  "url": "https://linkedin.com/in/sarah-grace-gruy-b1aa14438"},
]
CONTACT_EMAIL = "sarahgruy@gmail.com"


@app.context_processor
def inject_globals():
    return {"socials": SOCIALS, "contact_email": CONTACT_EMAIL}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


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
    msg["Reply-To"] = sender_email          # hitting "Reply" in Gmail answers the visitor
    msg.set_content(
        f"Name: {first} {last}\n"
        f"Email: {sender_email}\n\n"
        f"Message:\n{message}\n"
    )
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
        server.login(gmail_address, app_password)
        server.send_message(msg)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if request.form.get('website', '').strip():
            return redirect(url_for('contact'))

        first = request.form.get('first_name', '').strip()
        last = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        if not (first and email and message) or '@' not in email:
            flash("Please fill in your name, a valid email and a message.", "error")
            return redirect(url_for('contact') + '#contact-form')
        if len(message) > 5000:
            flash("That message is a little too long. Please shorten it.", "error")
            return redirect(url_for('contact') + '#contact-form')

        try:
            send_to_gmail(first, last, email, message)
        except Exception as exc:  # noqa: BLE001 - show a friendly message instead of crashing
            app.logger.error("Contact form email failed: %s", exc)
            flash(f"Sorry, your message couldn't be sent right now. "
                  f"You can email me directly at {CONTACT_EMAIL}.", "error")
        else:
            flash("Thank you! Your message has been sent. I'll reply soon.", "success")
        return redirect(url_for('contact') + '#contact-form')

    return render_template('contact.html')


@app.route('/works')
def works():
    return render_template('works.html')


@app.route('/works/touppercase', methods=['GET', 'POST'])
def touppercase():
    result = None
    if request.method == 'POST':
        input_string = request.form.get('inputString', '')
        result = input_string.upper()
    return render_template('touppercase.html', result=result)


@app.route('/works/area/circle', methods=['GET', 'POST'])
def acircle():
    result = None
    if request.method == 'POST':
        radius = float(request.form.get('radius', 0) or 0)
        result = 3.14 * radius * radius
    return render_template('circle.html', result=result)


@app.route('/works/area/triangle', methods=['GET', 'POST'])
def atriangle():
    result = None
    if request.method == 'POST':
        base = float(request.form.get('base', 0) or 0)
        height = float(request.form.get('height', 0) or 0)
        result = 0.5 * base * height
    return render_template('triangle.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
