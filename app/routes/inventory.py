from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.db import execute_query
from utils import login_required

inventory_bp = Blueprint('inventory', __name__)

FOOD_CATEGORIES = [
    'Rice', 'Wheat', 'Pulses', 'Canned Food',
    'Cooking Oil', 'Milk Powder', 'Baby Food', 'Hygiene Kits',
]


@inventory_bp.route('/')
def list_inventory():
    inventory = execute_query('SELECT * FROM food_inventory ORDER BY food_category')
    return render_template('inventory/list.html', inventory=inventory)


@inventory_bp.route('/update/<food_category>', methods=['GET', 'POST'])
@login_required
def update(food_category):
    rows = execute_query('SELECT * FROM food_inventory WHERE food_category = %s', (food_category,))
    if not rows:
        flash(f'Food category {food_category} not found.', 'danger')
        return redirect(url_for('inventory.list_inventory'))

    item = rows[0]

    if request.method == 'POST':
        action = request.form.get('action', 'add')
        amount = int(request.form.get('amount', 0))

        if action == 'add':
            new_units = item['units'] + amount
            change = amount
        else:
            new_units = max(0, item['units'] - amount)
            change = -(item['units'] - new_units)

        execute_query(
            'UPDATE food_inventory SET units = %s WHERE food_category = %s',
            (new_units, food_category),
            fetch=False,
        )
        execute_query(
            'INSERT INTO inventory_history (food_category, change_amount, units_after, reason) VALUES (%s, %s, %s, %s)',
            (food_category, change, new_units, 'Manual update'),
            fetch=False,
        )
        flash(f'{food_category} inventory updated to {new_units} units.', 'success')
        return redirect(url_for('inventory.list_inventory'))

    return render_template('inventory/update.html', item=item)


@inventory_bp.route('/history')
def history():
    food_category = request.args.get('food_category', 'Rice')
    records = execute_query(
        'SELECT * FROM inventory_history WHERE food_category = %s ORDER BY recorded_at DESC LIMIT 30',
        (food_category,),
    )
    labels = [str(r['recorded_at']) for r in reversed(records)]
    data = [r['units_after'] for r in reversed(records)]
    return render_template(
        'inventory/history.html',
        food_category=food_category,
        food_categories=FOOD_CATEGORIES,
        records=records,
        labels=labels,
        data=data,
    )
