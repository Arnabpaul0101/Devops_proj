from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.db import execute_query
from utils import login_required, contribution_status

contributors_bp = Blueprint('contributors', __name__)

FOOD_CATEGORIES = [
    'Rice', 'Wheat', 'Pulses', 'Canned Food',
    'Cooking Oil', 'Milk Powder', 'Baby Food', 'Hygiene Kits',
]


@contributors_bp.route('/')
def list_contributors():
    food_category = request.args.get('food_category', '')
    if food_category:
        contributors = execute_query(
            'SELECT * FROM contributors WHERE food_category = %s ORDER BY name', (food_category,)
        )
    else:
        contributors = execute_query('SELECT * FROM contributors ORDER BY name')

    for d in contributors:
        d['eligibility'] = contribution_status(d.get('last_contributed'))

    return render_template(
        'contributors/list.html',
        contributors=contributors,
        food_categories=FOOD_CATEGORIES,
        selected=food_category,
    )


@contributors_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        food_category = request.form.get('food_category', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        city = request.form.get('city', '').strip()
        last_contributed = request.form.get('last_contributed') or None

        if not name or not age or not food_category or not phone:
            flash('Name, age, food category, and phone are required.', 'danger')
            return render_template('contributors/register.html', food_categories=FOOD_CATEGORIES), 400

        execute_query(
            '''INSERT INTO contributors (name, age, food_category, phone, email, city, last_contributed)
               VALUES (%s, %s, %s, %s, %s, %s, %s)''',
            (name, int(age), food_category, phone, email or None, city or None, last_contributed),
            fetch=False,
        )
        flash(f'Contributor {name} registered successfully!', 'success')
        return redirect(url_for('contributors.list_contributors'))

    return render_template('contributors/register.html', food_categories=FOOD_CATEGORIES)


@contributors_bp.route('/<int:contributor_id>')
def detail(contributor_id):
    rows = execute_query('SELECT * FROM contributors WHERE id = %s', (contributor_id,))
    if not rows:
        return render_template('404.html'), 404
    contributor = rows[0]
    contributor['eligibility'] = contribution_status(contributor.get('last_contributed'))
    return render_template('contributors/detail.html', contributor=contributor)
