from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.db import execute_query
from utils import login_required

hospitals_bp = Blueprint('hospitals', __name__)


@hospitals_bp.route('/')
def list_hospitals():
    hospitals = execute_query('SELECT * FROM hospitals ORDER BY name')
    return render_template('hospitals/list.html', hospitals=hospitals)


@hospitals_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        city = request.form.get('city', '').strip()

        if not name or not phone:
            flash('Hospital name and phone are required.', 'danger')
            return render_template('hospitals/register.html'), 400

        execute_query(
            'INSERT INTO hospitals (name, address, phone, email, city) VALUES (%s, %s, %s, %s, %s)',
            (name, address or None, phone, email or None, city or None),
            fetch=False,
        )
        flash(f'Hospital "{name}" registered successfully!', 'success')
        return redirect(url_for('hospitals.list_hospitals'))

    return render_template('hospitals/register.html')


@hospitals_bp.route('/delete/<int:hospital_id>', methods=['POST'])
@login_required
def delete(hospital_id):
    execute_query('DELETE FROM hospitals WHERE id = %s', (hospital_id,), fetch=False)
    flash('Hospital removed.', 'info')
    return redirect(url_for('hospitals.list_hospitals'))
