import os 

from flask import (Flask, render_template, request, redirect, url_for, flash)

from routes.socials import SOCIALS, CONTACT_EMAIL, send_to_gmail
from routes.Lab_3 import linked_bp
from routes.stack import stack_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.register_blueprint(linked_bp)
app.register_blueprint(stack_bp)

@app.context_processor
def inject_globals():
    return {"socials": SOCIALS, "contact_email": CONTACT_EMAIL}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


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
        except Exception as exc: 
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
