from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.db import execute_query
from utils import login_required, send_notification

requests_bp = Blueprint('requests', __name__)

BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']


@requests_bp.route('/')
def list_requests():
    blood_requests = execute_query('SELECT * FROM blood_requests ORDER BY requested_at DESC')
    return render_template('requests/list.html', blood_requests=blood_requests)


@requests_bp.route('/new', methods=['GET', 'POST'])
def new_request():
    hospitals = execute_query('SELECT id, name FROM hospitals ORDER BY name')

    if request.method == 'POST':
        patient_name = request.form.get('patient_name', '').strip()
        blood_type = request.form.get('blood_type', '').strip()
        units_required = request.form.get('units_required', '').strip()
        hospital = request.form.get('hospital', '').strip()
        hospital_id = request.form.get('hospital_id') or None
        contact_phone = request.form.get('contact_phone', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        urgency = request.form.get('urgency', 'normal')

        if not patient_name or not blood_type or not units_required or not contact_phone:
            flash('Patient name, blood type, units, and phone are required.', 'danger')
            return render_template('requests/new.html', blood_types=BLOOD_TYPES, hospitals=hospitals), 400

        execute_query(
            '''INSERT INTO blood_requests
               (patient_name, blood_type, units_required, hospital, hospital_id,
                contact_phone, contact_email, urgency)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (patient_name, blood_type, int(units_required),
             hospital or None, hospital_id, contact_phone,
             contact_email or None, urgency),
            fetch=False,
        )
        flash(f'Blood request for {patient_name} submitted!', 'success')
        return redirect(url_for('requests.list_requests'))

    return render_template('requests/new.html', blood_types=BLOOD_TYPES, hospitals=hospitals)


@requests_bp.route('/approve/<int:request_id>', methods=['POST'])
@login_required
def approve(request_id):
    rows = execute_query('SELECT * FROM blood_requests WHERE id = %s', (request_id,))
    if not rows:
        flash('Request not found.', 'danger')
        return redirect(url_for('requests.list_requests'))

    req = rows[0]
    inventory = execute_query('SELECT * FROM blood_inventory WHERE blood_type = %s', (req['blood_type'],))

    if not inventory or inventory[0]['units'] < req['units_required']:
        flash(f'Insufficient {req["blood_type"]} units in inventory.', 'danger')
        return redirect(url_for('requests.list_requests'))

    new_units = inventory[0]['units'] - req['units_required']
    execute_query(
        'UPDATE blood_inventory SET units = %s WHERE blood_type = %s',
        (new_units, req['blood_type']), fetch=False,
    )
    execute_query(
        'INSERT INTO inventory_history (blood_type, change_amount, units_after, reason) VALUES (%s, %s, %s, %s)',
        (req['blood_type'], -req['units_required'], new_units, f'Request #{request_id} approved'),
        fetch=False,
    )
    execute_query(
        "UPDATE blood_requests SET status='approved', resolved_at=%s WHERE id=%s",
        (datetime.now(), request_id), fetch=False,
    )

    if req.get('contact_email'):
        send_notification(
            subject=f'Blood Request #{request_id} Approved',
            recipient=req['contact_email'],
            body_html=f'''
                <h2 style="color:#2ecc71;">Your blood request has been approved!</h2>
                <p>Dear <strong>{req["patient_name"]}</strong>,</p>
                <p>Your request for <strong>{req["units_required"]} units of {req["blood_type"]}</strong>
                   has been <strong style="color:#2ecc71;">approved</strong>.</p>
                <p>Please contact the blood bank to arrange collection.</p>
                <br><p>Blood Bank Management System</p>
            ''',
        )

    flash(f'Request #{request_id} approved. Inventory updated.', 'success')
    return redirect(url_for('requests.list_requests'))


@requests_bp.route('/reject/<int:request_id>', methods=['POST'])
@login_required
def reject(request_id):
    rows = execute_query('SELECT * FROM blood_requests WHERE id = %s', (request_id,))
    if rows and rows[0].get('contact_email'):
        req = rows[0]
        send_notification(
            subject=f'Blood Request #{request_id} Update',
            recipient=req['contact_email'],
            body_html=f'''
                <h2 style="color:#e74c3c;">Blood Request Update</h2>
                <p>Dear <strong>{req["patient_name"]}</strong>,</p>
                <p>Unfortunately, your request for <strong>{req["units_required"]} units of
                   {req["blood_type"]}</strong> could not be fulfilled at this time.</p>
                <p>Please contact us for further assistance.</p>
                <br><p>Blood Bank Management System</p>
            ''',
        )

    execute_query(
        "UPDATE blood_requests SET status='rejected', resolved_at=%s WHERE id=%s",
        (datetime.now(), request_id), fetch=False,
    )
    flash(f'Request #{request_id} rejected.', 'warning')
    return redirect(url_for('requests.list_requests'))
