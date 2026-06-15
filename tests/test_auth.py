def test_admin_can_log_in(client):
    response = client.post(
        '/auth/login',
        data={'username': 'admin', 'password': 'admin123'},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')

    with client.session_transaction() as session:
        assert session['admin_logged_in'] is True
        assert session['admin_username'] == 'admin'


def test_admin_login_rejects_invalid_password(client):
    response = client.post(
        '/auth/login',
        data={'username': 'admin', 'password': 'wrong-password'},
    )

    assert response.status_code == 200
    assert b'Invalid username or password.' in response.data
