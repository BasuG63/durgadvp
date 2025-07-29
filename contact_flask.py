
from flask import Flask, request, render_template_string, render_template, jsonify, send_from_directory
import smtplib
from email.mime.text import MIMEText
import os
import ssl
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Simple HTML form for testing (remove if using AJAX from your site)
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
  <title>Contact Form</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"/>
  <script>
    // Disable right-click context menu
    document.addEventListener('DOMContentLoaded', function() {
      document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
      });
      // Attempt to block PrintScreen key (not foolproof)
      document.addEventListener('keydown', function(e) {
        if (e.key === 'PrintScreen') {
          e.preventDefault();
          alert('Screenshots are disabled on this site.');
          // Attempt to clear clipboard (works in some browsers)
          navigator.clipboard.writeText('Screenshots are disabled on this site.');
        }
        // Attempt to block Ctrl+Shift+I, Ctrl+Shift+C, F12 (dev tools)
        if ((e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'C')) || e.key === 'F12') {
          e.preventDefault();
        }
      });
      // Attempt to blur the page if screenshot tools are detected (not foolproof)
      document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'hidden') {
          document.body.style.filter = 'blur(8px)';
        } else {
          document.body.style.filter = '';
        }
      });
    });
  </script>
</head>
<body oncontextmenu="return false;">
<form method="post" class="contact-form" style="max-width:400px;margin:2rem auto;padding:2rem;background:#fffbe7;border-radius:1rem;box-shadow:0 2px 12px rgba(224,126,60,0.10);">
  <label>Name: <input name="name" required></label><br><br>
  <label>Email: <input name="email" type="email" required></label><br><br>
  <label>Phone: <input name="phone" type="tel" pattern="\d{10}" maxlength="10" minlength="10" required placeholder="10-digit phone"></label><br><br>
  <label>Message:<br><textarea name="message" required style="width:100%;height:80px;"></textarea></label><br><br>
  <button type="submit" class="btn btn-primary">Send</button>
</form>
{% if msg %}<p style="text-align:center;">{{msg}}</p>{% endif %}
</body>
</html>
"""

# Configure your SMTP server here
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.environ.get("SMTP_USER", "basavarajagurikar2004@gmail.com")  # Your Gmail address
SMTP_PASS = os.environ.get("SMTP_PASS")  # Your Gmail App Password (set as env variable)
TO_EMAIL = os.environ.get("TO_EMAIL", "sharanappag9900@gmail.com")   # Recipient (your Gmail)

import re

def send_email(name, email, phone, message):
    subject = f"New Contact Form Submission from {name}"
    body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = TO_EMAIL

    # Confirmation email to candidate
    confirm_subject = "Thank you for contacting DURGA DEVELOPERS &Basava Enterprises"
    confirm_body = f"Dear {name},\n\nThank you for reaching out to us! We have received your message and will get back to you soon.\n\nYour details:\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}\n\nBest regards,\nDURGA DEVELOPERS &Basava Enterprises Team"
    confirm_msg = MIMEText(confirm_body)
    confirm_msg['Subject'] = confirm_subject
    confirm_msg['From'] = SMTP_USER
    confirm_msg['To'] = email

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())  # Admin
            server.sendmail(SMTP_USER, email, confirm_msg.as_string())  # Candidate
        print("Email sent successfully!")
    except Exception as e:
        print("Email send error:", e)
        raise

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        # Validate phone number
        if not phone or not re.fullmatch(r"\d{10}", phone):
            return render_template_string(HTML_FORM, msg="Invalid phone number. Please enter a 10-digit number.")
        try:
            send_email(name, email, phone, message)
            return render_template_string(HTML_FORM, msg="Message sent successfully!")
        except Exception as e:
            return render_template_string(HTML_FORM, msg=f"Failed to send message. Error: {e}")
    return render_template_string(HTML_FORM, msg=None)

# For AJAX/JS frontend (returns JSON)
@app.route("/api/contact", methods=["POST"])
def api_contact():
    data = request.json
    try:
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        message = data.get("message")
        if not phone or not re.fullmatch(r"\d{10}", phone):
            return jsonify({"success": False, "error": "Invalid phone number. Please enter a 10-digit number."}), 400
        send_email(name, email, phone, message)
        return jsonify({"success": True})
    except Exception as e:
        print("API email send error:", e)
        return jsonify({"success": False, "error": str(e)}), 500
@app.route("/test_email")
def test_email():
    try:
        send_email("Test User", "test@example.com", "9876543210", "This is a test email from Flask app.")
        return "Test email sent successfully! Check your inbox."
    except Exception as e:
        return f"Failed to send test email. Error: {e}"



# Serve main pages using render_template (templates must be in the 'templates' folder)

# Helper to inject security JS into all templates
SECURITY_JS = '''<script>
  document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('contextmenu', function(e) { e.preventDefault(); });
    document.addEventListener('keydown', function(e) {
      if (e.key === 'PrintScreen') {
        e.preventDefault();
        alert('Screenshots are disabled on this site.');
        navigator.clipboard.writeText('Screenshots are disabled on this site.');
      }
      if ((e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'C')) || e.key === 'F12') {
        e.preventDefault();
      }
    });
    document.addEventListener('visibilitychange', function() {
      if (document.visibilityState === 'hidden') {
        document.body.style.filter = 'blur(8px)';
      } else {
        document.body.style.filter = '';
      }
    });
  });
</script>'''

def render_secure_template(template_name, **context):
    if 'security_js' not in context:
        context['security_js'] = SECURITY_JS
    return render_template(template_name, **context)

@app.route("/")
def home():
    return render_secure_template("index.html")

@app.route("/services.html")
def services():
    return render_secure_template("services.html")

@app.route("/roadproject.html")
def roadproject():
    return render_secure_template("roadproject.html")

@app.route("/realestate.html")
def realestate():
    return render_secure_template("realestate.html")



if __name__ == "__main__":
    app.run(debug=False)
