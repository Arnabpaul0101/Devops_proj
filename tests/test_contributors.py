import pytest


SAMPLE_CONTRIBUTOR = {
    'id': 1, 'name': 'Rahul Singh', 'age': 28, 'food_category': 'Milk Powder',
    'phone': '9876543210', 'email': 'rahul@example.com',
    'city': 'Delhi', 'last_contributed': None, 'created_at': '2024-01-01',
}


def test_contributor_list_page_loads(client, mocker):
    mocker.patch('routes.contributors.execute_query', return_value=[SAMPLE_CONTRIBUTOR])
    response = client.get('/contributors/')
    assert response.status_code == 200
    assert b'Rahul Singh' in response.data


def test_register_form_loads(client):
    response = client.get('/contributors/register')
    assert response.status_code == 200
    assert b'Register New Contributor' in response.data


def test_register_contributor_valid_data(client, mocker):
    mocker.patch('routes.contributors.execute_query', return_value=1)
    response = client.post('/contributors/register', data={
        'name': 'Priya Sharma',
        'age': '25',
        'food_category': 'Rice',
        'phone': '9123456789',
        'email': 'priya@example.com',
        'city': 'Mumbai',
        'last_contributed': '',
    })
    assert response.status_code == 302


def test_register_contributor_missing_required_fields(client):
    response = client.post('/contributors/register', data={
        'name': '',
        'age': '',
        'food_category': '',
        'phone': '',
    })
    assert response.status_code == 400
