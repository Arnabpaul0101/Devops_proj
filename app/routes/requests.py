from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import execute_query
from datetime import datetime

requests_bp = Blueprint('requests', __name__)

BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']


@requests_bp.route('/')
def list_requests():
    blood_requests = execute_query(
        'SELECT * FROM blood_requests ORDER BY requested_at DESC'
    )
    return render_template('requests/list.html', blood_requests=blood_requests)


@requests_bp.route('/new', methods=['GET', 'POST'])
def new_request():
    if request.method == 'POST':
        patient_name = request.form.get('patient_name', '').strip()
        blood_type = request.form.get('blood_type', '').strip()
        units_required = request.form.get('units_required', '').strip()
        hospital = request.form.get('hospital', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        urgency = request.form.get('urgency', 'normal')

        if not patient_name or not blood_type or not units_required or not contact_phone:
            flash('Patient name, blood type, units required, and contact phone are required.', 'danger')
            return render_template('requests/new.html', blood_types=BLOOD_TYPES), 400

        execute_query(
            '''INSERT INTO blood_requests
               (patient_name, blood_type, units_required, hospital, contact_phone, urgency)
               VALUES (%s, %s, %s, %s, %s, %s)''',
            (patient_name, blood_type, int(units_required), hospital or None, contact_phone, urgency),
            fetch=False,
        )
        flash(f'Blood request for {patient_name} submitted successfully!', 'success')
        return redirect(url_for('requests.list_requests'))

    return render_template('requests/new.html', blood_types=BLOOD_TYPES)


@requests_bp.route('/approve/<int:request_id>', methods=['POST'])
def approve(request_id):
    rows = execute_query('SELECT * FROM blood_requests WHERE id = %s', (request_id,))
    if not rows:
        flash('Request not found.', 'danger')
        return redirect(url_for('requests.list_requests'))

    req = rows[0]
    inventory = execute_query(
        'SELECT * FROM blood_inventory WHERE blood_type = %s', (req['blood_type'],)
    )

    if not inventory or inventory[0]['units'] < req['units_required']:
        flash(f'Insufficient {req["blood_type"]} units in inventory.', 'danger')
        return redirect(url_for('requests.list_requests'))

    execute_query(
        'UPDATE blood_inventory SET units = units - %s WHERE blood_type = %s',
        (req['units_required'], req['blood_type']),
        fetch=False,
    )
    execute_query(
        "UPDATE blood_requests SET status='approved', resolved_at=%s WHERE id=%s",
        (datetime.now(), request_id),
        fetch=False,
    )
    flash(f'Request #{request_id} approved. Inventory updated.', 'success')
    return redirect(url_for('requests.list_requests'))


@requests_bp.route('/reject/<int:request_id>', methods=['POST'])
def reject(request_id):
    execute_query(
        "UPDATE blood_requests SET status='rejected', resolved_at=%s WHERE id=%s",
        (datetime.now(), request_id),
        fetch=False,
    )
    flash(f'Request #{request_id} rejected.', 'warning')
    return redirect(url_for('requests.list_requests'))
