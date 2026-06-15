from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.db import execute_query
from utils import login_required

requests_bp = Blueprint('requests', __name__)

FOOD_CATEGORIES = [
    'Rice', 'Wheat', 'Pulses', 'Canned Food',
    'Cooking Oil', 'Milk Powder', 'Baby Food', 'Hygiene Kits',
]


@requests_bp.route('/')
def list_requests():
    food_requests = execute_query('SELECT * FROM food_requests ORDER BY requested_at DESC')
    return render_template('requests/list.html', food_requests=food_requests)


@requests_bp.route('/new', methods=['GET', 'POST'])
def new_request():
    agencies = execute_query('SELECT id, name FROM agencies ORDER BY name')

    if request.method == 'POST':
        beneficiary_name = request.form.get('beneficiary_name', '').strip()
        food_category = request.form.get('food_category', '').strip()
        units_required = request.form.get('units_required', '').strip()
        agency = request.form.get('agency', '').strip()
        agency_id = request.form.get('agency_id') or None
        contact_phone = request.form.get('contact_phone', '').strip()
        urgency = request.form.get('urgency', 'normal')

        if not beneficiary_name or not food_category or not units_required or not contact_phone:
            flash('Beneficiary name, food category, units, and phone are required.', 'danger')
            return render_template('requests/new.html', food_categories=FOOD_CATEGORIES, agencies=agencies), 400

        execute_query(
            '''INSERT INTO food_requests
               (beneficiary_name, food_category, units_required, agency, agency_id,
                contact_phone, urgency)
               VALUES (%s, %s, %s, %s, %s, %s, %s)''',
            (beneficiary_name, food_category, int(units_required),
             agency or None, agency_id, contact_phone, urgency),
            fetch=False,
        )
        flash(f'Food request for {beneficiary_name} submitted!', 'success')
        return redirect(url_for('requests.list_requests'))

    return render_template('requests/new.html', food_categories=FOOD_CATEGORIES, agencies=agencies)


@requests_bp.route('/approve/<int:request_id>', methods=['POST'])
@login_required
def approve(request_id):
    rows = execute_query('SELECT * FROM food_requests WHERE id = %s', (request_id,))
    if not rows:
        flash('Request not found.', 'danger')
        return redirect(url_for('requests.list_requests'))

    req = rows[0]
    inventory = execute_query('SELECT * FROM food_inventory WHERE food_category = %s', (req['food_category'],))

    if not inventory or inventory[0]['units'] < req['units_required']:
        flash(f'Insufficient {req["food_category"]} units in inventory.', 'danger')
        return redirect(url_for('requests.list_requests'))

    new_units = inventory[0]['units'] - req['units_required']
    execute_query(
        'UPDATE food_inventory SET units = %s WHERE food_category = %s',
        (new_units, req['food_category']), fetch=False,
    )
    execute_query(
        'INSERT INTO inventory_history (food_category, change_amount, units_after, reason) VALUES (%s, %s, %s, %s)',
        (req['food_category'], -req['units_required'], new_units, f'Request #{request_id} approved'),
        fetch=False,
    )
    execute_query(
        "UPDATE food_requests SET status='approved', resolved_at=%s WHERE id=%s",
        (datetime.now(), request_id), fetch=False,
    )
    flash(f'Request #{request_id} approved. Inventory updated.', 'success')
    return redirect(url_for('requests.list_requests'))


@requests_bp.route('/reject/<int:request_id>', methods=['POST'])
@login_required
def reject(request_id):
    execute_query(
        "UPDATE food_requests SET status='rejected', resolved_at=%s WHERE id=%s",
        (datetime.now(), request_id), fetch=False,
    )
    flash(f'Request #{request_id} rejected.', 'warning')
    return redirect(url_for('requests.list_requests'))
