import pytest


SAMPLE_INVENTORY = [
    {'id': 1, 'blood_type': 'A+', 'units': 10, 'updated_at': '2024-01-01'},
    {'id': 2, 'blood_type': 'O+', 'units': 3, 'updated_at': '2024-01-01'},
]


def test_inventory_page_loads(client, mocker):
    mocker.patch('models.db.execute_query', return_value=SAMPLE_INVENTORY)
    response = client.get('/inventory/')
    assert response.status_code == 200
    assert b'Blood Inventory' in response.data


def test_update_form_loads(client, mocker):
    mocker.patch('routes.inventory.execute_query', return_value=[SAMPLE_INVENTORY[0]])
    response = client.get('/inventory/update/A+')
    assert response.status_code == 200
    assert b'Update Inventory' in response.data


def test_update_inventory_valid(client, mocker):
    mocker.patch('models.db.execute_query', side_effect=[
        [SAMPLE_INVENTORY[0]],
        1,
    ])
    response = client.post('/inventory/update/A+', data={'action': 'add', 'amount': '5'})
    assert response.status_code == 302
