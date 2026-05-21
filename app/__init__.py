from flask import Flask, render_template, request

from config import config_map
from models.db import execute_query


def ensure_schema(app):
    """Create any missing tables/columns for existing databases."""
    if app.config.get('TESTING'):
        return
    with app.app_context(): 
        try:
            execute_query('''
                CREATE TABLE IF NOT EXISTS agencies (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(150) NOT NULL,
                    address VARCHAR(255),
                    phone VARCHAR(15) NOT NULL,
                    email VARCHAR(100),
                    city VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''', fetch=False)

            execute_query('''
                CREATE TABLE IF NOT EXISTS inventory_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    food_category VARCHAR(50) NOT NULL,
                    change_amount INT NOT NULL,
                    units_after INT NOT NULL,
                    reason VARCHAR(150),
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''', fetch=False)

            cols = execute_query('''
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'food_requests'
            ''')
            col_names = [c['COLUMN_NAME'] for c in cols]

            if 'contact_email' not in col_names:
                execute_query(
                    'ALTER TABLE food_requests ADD COLUMN contact_email VARCHAR(100)',
                    fetch=False,
                )
            if 'agency_id' not in col_names:
                execute_query(
                    'ALTER TABLE food_requests ADD COLUMN agency_id INT NULL',
                    fetch=False,
                )
        except Exception as e:
            app.logger.warning(f'Schema migration: {e}')


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    from routes.auth import auth_bp
    from routes.contributors import contributors_bp
    from routes.agencies import agencies_bp
    from routes.inventory import inventory_bp
    from routes.requests import requests_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(contributors_bp, url_prefix='/contributors')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(requests_bp, url_prefix='/requests')
    app.register_blueprint(agencies_bp, url_prefix='/agencies')

    ensure_schema(app)

    @app.route('/')
    def dashboard():
        contributor_count = execute_query('SELECT COUNT(*) AS cnt FROM contributors')[0]['cnt']
        total_units = execute_query('SELECT COALESCE(SUM(units), 0) AS total FROM food_inventory')[0]['total']
        pending_count = execute_query(
            "SELECT COUNT(*) AS cnt FROM food_requests WHERE status='pending'"
        )[0]['cnt']
        agency_count = execute_query('SELECT COUNT(*) AS cnt FROM agencies')[0]['cnt']
        low_stock = execute_query(
            'SELECT food_category, units FROM food_inventory WHERE units < 5 ORDER BY units'
        )
        inventory = execute_query('SELECT food_category, units FROM food_inventory ORDER BY food_category')
        return render_template(
            'index.html',
            contributor_count=contributor_count,
            total_units=total_units,
            pending_count=pending_count,
            agency_count=agency_count,
            low_stock=low_stock,
            inventory=inventory,
        )

    @app.route('/search')
    def search():
        q = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'contributor')
        results = []
        if q:
            if search_type == 'contributor':
                results = execute_query(
                    'SELECT * FROM contributors WHERE food_category = %s ORDER BY name', (q,)
                )
            else:
                results = execute_query(
                    'SELECT * FROM food_inventory WHERE food_category = %s', (q,)
                )
        return render_template('search.html', results=results, q=q, search_type=search_type)

    return app
