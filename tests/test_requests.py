import pytest


SAMPLE_REQUEST = {
    'id': 1, 'beneficiary_name': 'Anita Patel', 'food_category': 'Pulses',
    'units_required': 2, 'agency': 'City Relief Kitchen', 'contact_phone': '9000000001',
    'urgency': 'urgent', 'status': 'pending',
    'requested_at': '2024-01-01', 'resolved_at': None,
}


def test_requests_list_loads(client, mocker):
    mocker.patch('routes.requests.execute_query', return_value=[SAMPLE_REQUEST])
    response = client.get('/requests/')
    assert response.status_code == 200
    assert b'Anita Patel' in response.data


def test_new_request_form_loads(client):
    from unittest.mock import patch
    with patch('routes.requests.execute_query', return_value=[]):
        response = client.get('/requests/new')
    assert response.status_code == 200
    assert b'New Food Request' in response.data


def test_create_request_valid(client, mocker):
    mocker.patch('routes.requests.execute_query', side_effect=[[], 1])
    response = client.post('/requests/new', data={
        'beneficiary_name': 'Suresh Kumar',
        'food_category': 'Baby Food',
        'units_required': '3',
        'agency': 'Hope Community Pantry',
        'contact_phone': '9111111111',
        'urgency': 'normal',
    })
    assert response.status_code == 302


def test_create_request_missing_fields(client):
    from unittest.mock import patch
    with patch('routes.requests.execute_query', return_value=[]):
        response = client.post('/requests/new', data={
            'beneficiary_name': '',
            'food_category': '',
            'units_required': '',
            'contact_phone': '',
        })
    assert response.status_code == 400
