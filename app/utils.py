from datetime import date
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
