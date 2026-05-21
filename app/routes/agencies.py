from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.db import execute_query
from utils import login_required

agencies_bp = Blueprint('agencies', __name__)


@agencies_bp.route('/')
def list_agencies():
    agencies = execute_query('SELECT * FROM agencies ORDER BY name')
    return render_template('agencies/list.html', agencies=agencies)


@agencies_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        city = request.form.get('city', '').strip()

        if not name or not phone:
            flash('Agency name and phone are required.', 'danger')
            return render_template('agencies/register.html'), 400

        execute_query(
            'INSERT INTO agencies (name, address, phone, email, city) VALUES (%s, %s, %s, %s, %s)',
            (name, address or None, phone, email or None, city or None),
            fetch=False,
        )
        flash(f'Agency "{name}" registered successfully!', 'success')
        return redirect(url_for('agencies.list_agencies'))

    return render_template('agencies/register.html')


@agencies_bp.route('/delete/<int:agency_id>', methods=['POST'])
@login_required
def delete(agency_id):
    execute_query('DELETE FROM agencies WHERE id = %s', (agency_id,), fetch=False)
    flash('Agency removed.', 'info')
    return redirect(url_for('agencies.list_agencies'))
