import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

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
