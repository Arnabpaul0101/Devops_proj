import sys
import os
import pytest

# Locally: app code is in ../app/ relative to this file
# In Docker: app code is in parent dir (tests/ is copied into /app/tests/)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(parent_dir, 'app')
if os.path.isdir(app_dir):
    sys.path.insert(0, app_dir)
else:
    sys.path.insert(0, parent_dir)

from __init__ import create_app


@pytest.fixture
def app(mocker):
    mocker.patch('models.db.get_connection')

    application = create_app('testing')
    application.config['TESTING'] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def make_db_return(mocker, rows):
    mocker.patch('models.db.execute_query', return_value=rows)


def make_db_write(mocker):
    mocker.patch('models.db.execute_query', return_value=1)
