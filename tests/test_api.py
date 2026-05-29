import pytest
from flask import Flask
from app.extensions import db, jwt, migrate, cors


def create_test_app():
    """Создание тестового приложения."""
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'JWT_ACCESS_TOKEN_EXPIRES': 3600,
        'CORS_ORIGINS': '*'
    })

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": '*'}})

    from app.api.v1 import api_v1_bp
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    @app.route('/')
    def index():
        return 'OK'

    return app


@pytest.fixture
def app():
    """Создание тестового приложения."""
    test_app = create_test_app()

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Создание тестового клиента."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Создание тестового runner."""
    return app.test_cli_runner()


class TestAuth:
    """Тесты для аутентификации."""

    def test_register_success(self, client):
        """Тест успешной регистрации."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
        assert data['user']['email'] == 'test@example.com'

    def test_register_duplicate_username(self, client):
        """Тест регистрации с дублирующимся username."""
        client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test1@example.com',
            'password': 'password123'
        })

        response = client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'password123'
        })

        assert response.status_code == 409
        assert b'already exists' in response.data

    def test_register_duplicate_email(self, client):
        """Тест регистрации с дублирующимся email."""
        client.post('/api/v1/auth/register', json={
            'username': 'testuser1',
            'email': 'test@example.com',
            'password': 'password123'
        })

        response = client.post('/api/v1/auth/register', json={
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'password123'
        })

        assert response.status_code == 409

    def test_register_invalid_email(self, client):
        """Тест регистрации с некорректным email."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'password123'
        })

        assert response.status_code == 400

    def test_register_short_password(self, client):
        """Тест регистрации с коротким паролем."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123'
        })

        assert response.status_code == 400

    def test_register_short_username(self, client):
        """Тест регистрации с коротким username."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'ab',
            'email': 'test@example.com',
            'password': 'password123'
        })

        assert response.status_code == 400

    def test_register_missing_fields(self, client):
        """Тест регистрации с пропущенными полями."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'testuser'
        })

        assert response.status_code == 400

    def test_login_success(self, client):
        """Тест успешного входа."""
        client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        response = client.post('/api/v1/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == 'testuser'

    def test_login_wrong_password(self, client):
        """Тест входа с неверным паролем."""
        client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        response = client.post('/api/v1/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Тест входа несуществующего пользователя."""
        response = client.post('/api/v1/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })

        assert response.status_code == 401


class TestProjects:
    """Тесты для проектов."""

    def test_create_project(self, client):
        """Тест создания проекта."""
        client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        login_response = client.post('/api/v1/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']

        response = client.post('/api/v1/projects',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'name': 'Test Project',
                'description': 'Test Description'
            }
        )

        assert response.status_code == 201
        data = response.get_json()
        assert 'project' in data
        assert data['project']['name'] == 'Test Project'

    def test_create_project_unauthorized(self, client):
        """Тест создания проекта без авторизации."""
        response = client.post('/api/v1/projects', json={
            'name': 'Test Project'
        })

        assert response.status_code == 401

    def test_get_projects(self, client):
        """Тест получения списка проектов."""
        client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        login_response = client.post('/api/v1/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']

        response = client.get('/api/v1/projects',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        assert 'projects' in response.get_json()


class TestTasks:
    """Тесты для задач."""

    def test_create_task(self, client):
        """Тест создания задачи."""
        client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        login_response = client.post('/api/v1/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']

        project_response = client.post('/api/v1/projects',
            headers={'Authorization': f'Bearer {token}'},
            json={'name': 'Test Project'}
        )
        project_id = project_response.get_json()['project']['id']

        response = client.post('/api/v1/tasks',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Task',
                'description': 'Task Description',
                'project_id': project_id
            }
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'Test Task'
        assert data['status'] == 'todo'

    def test_create_subtask(self, client):
        """Тест создания подзадачи."""
        client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        login_response = client.post('/api/v1/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']

        project_response = client.post('/api/v1/projects',
            headers={'Authorization': f'Bearer {token}'},
            json={'name': 'Test Project'}
        )
        project_id = project_response.get_json()['project']['id']

        task_response = client.post('/api/v1/tasks',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Parent Task',
                'project_id': project_id
            }
        )
        task_id = task_response.get_json()['id']

        subtask_response = client.post('/api/v1/tasks',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Subtask',
                'project_id': project_id,
                'parent_id': task_id
            }
        )

        assert subtask_response.status_code == 201

    def test_get_project_tasks(self, client):
        """Тест получения задач проекта."""
        client.post('/api/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        login_response = client.post('/api/v1/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']

        project_response = client.post('/api/v1/projects',
            headers={'Authorization': f'Bearer {token}'},
            json={'name': 'Test Project'}
        )
        project_id = project_response.get_json()['project']['id']

        client.post('/api/v1/tasks',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Task',
                'project_id': project_id
            }
        )

        response = client.get(f'/api/v1/tasks/project/{project_id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'tasks' in data
        assert len(data['tasks']) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])