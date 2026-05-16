from flask import Flask, render_template, request
from config import config_map
from models.db import execute_query


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    from routes.donors import donors_bp
    from routes.inventory import inventory_bp
    from routes.requests import requests_bp

    app.register_blueprint(donors_bp, url_prefix='/donors')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(requests_bp, url_prefix='/requests')

    @app.route('/')
    def dashboard():
        donor_count = execute_query('SELECT COUNT(*) AS cnt FROM donors')[0]['cnt']
        total_units = execute_query('SELECT COALESCE(SUM(units), 0) AS total FROM blood_inventory')[0]['total']
        pending_count = execute_query(
            "SELECT COUNT(*) AS cnt FROM blood_requests WHERE status='pending'"
        )[0]['cnt']
        return render_template(
            'index.html',
            donor_count=donor_count,
            total_units=total_units,
            pending_count=pending_count,
        )

    @app.route('/search')
    def search():
        q = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'donor')
        results = []
        if q:
            if search_type == 'donor':
                results = execute_query(
                    'SELECT * FROM donors WHERE blood_type = %s ORDER BY name', (q,)
                )
            else:
                results = execute_query(
                    'SELECT * FROM blood_inventory WHERE blood_type = %s', (q,)
                )
        return render_template('search.html', results=results, q=q, search_type=search_type)

    return app
