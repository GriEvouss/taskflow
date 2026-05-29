from tests.test_api import create_test_app, db

app = create_test_app()
with app.app_context():
    db.create_all()
    client = app.test_client()

    r = client.post('/api/v1/auth/register', json={
        'username': 'test',
        'email': 'test@test.com',
        'password': 'password123'
    })
    print('Register:', r.status_code, r.get_json())

    r = client.post('/api/v1/auth/login', json={
        'username': 'test',
        'password': 'password123'
    })
    print('Login:', r.status_code, r.get_json())
    token = r.get_json()['access_token']

    r = client.post('/api/v1/projects',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Test Project'}
    )
    print('Create project:', r.status_code, r.get_json())