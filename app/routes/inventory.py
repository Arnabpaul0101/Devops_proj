from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import execute_query

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/')
def list_inventory():
    inventory = execute_query('SELECT * FROM blood_inventory ORDER BY blood_type')
    return render_template('inventory/list.html', inventory=inventory)


@inventory_bp.route('/update/<blood_type>', methods=['GET', 'POST'])
def update(blood_type):
    rows = execute_query(
        'SELECT * FROM blood_inventory WHERE blood_type = %s', (blood_type,)
    )
    if not rows:
        flash(f'Blood type {blood_type} not found.', 'danger')
        return redirect(url_for('inventory.list_inventory'))

    item = rows[0]

    if request.method == 'POST':
        action = request.form.get('action', 'add')
        amount = int(request.form.get('amount', 0))

        if action == 'add':
            new_units = item['units'] + amount
        else:
            new_units = max(0, item['units'] - amount)

        execute_query(
            'UPDATE blood_inventory SET units = %s WHERE blood_type = %s',
            (new_units, blood_type),
            fetch=False,
        )
        flash(f'Inventory for {blood_type} updated to {new_units} units.', 'success')
        return redirect(url_for('inventory.list_inventory'))

    return render_template('inventory/update.html', item=item)
