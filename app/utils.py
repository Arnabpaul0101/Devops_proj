import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps

from flask import current_app, flash, redirect, session, url_for


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_app.config.get('BYPASS_LOGIN'):
            return f(*args, **kwargs)
        if not session.get('admin_logged_in'):
            flash('Please log in as admin to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def donor_eligibility(last_donated):
    """Returns 'eligible', 'ineligible', or 'unknown'."""
    if last_donated is None:
        return 'unknown'
    if isinstance(last_donated, str):
        from datetime import datetime
        try:
            last_donated = datetime.strptime(str(last_donated), '%Y-%m-%d').date()
        except ValueError:
            return 'unknown'
    days = (date.today() - last_donated).days
    return 'eligible' if days >= 90 else 'ineligible'


def send_notification(subject, recipient, body_html):
    if not recipient:
        return
    server_addr = current_app.config.get('MAIL_SERVER')
    username = current_app.config.get('MAIL_USERNAME')
    password = current_app.config.get('MAIL_PASSWORD')
    port = current_app.config.get('MAIL_PORT', 587)

    if not server_addr or not username or not password:
        current_app.logger.info(f'Email skipped (not configured): {subject}')
        return

    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = username
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html'))
        with smtplib.SMTP(server_addr, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        current_app.logger.info(f'Email sent to {recipient}: {subject}')
    except Exception as e:
        current_app.logger.warning(f'Email failed: {e}')
