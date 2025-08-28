import pytest
import os
import tempfile
from app import create_app
from extensions import db
from models import User, Profile, Settings


@pytest.fixture
def app():
    """Create and configure a test Flask app."""
    # Create a temporary file to isolate database during tests
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'TESTING': True,
        'DISABLE_EXTERNAL_CALLS': True,
        'OFFLINE_MODE': True
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the Flask app."""
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    """Authentication helper for tests."""
    class AuthActions:
        def __init__(self, client):
            self._client = client

        def register(self, username='testuser', password='testpass123'):
            return self._client.post(
                '/auth/register',
                data={'username': username, 'password': password}
            )

        def login(self, username='testuser', password='testpass123'):
            return self._client.post(
                '/auth/login',
                data={'username': username, 'password': password}
            )

        def logout(self):
            return self._client.get('/auth/logout')

    return AuthActions(client)


@pytest.fixture
def user(app):
    """Create a test user with profile."""
    with app.app_context():
        user = User(username='testuser')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        
        # Create profile
        profile = Profile(
            user_id=user.id,
            name='Test User',
            age=30,
            sex='male',
            height_cm=175,
            weight_kg=75,
            activity_level='moderate',
            goal_type='maintain',
            budget_range='medium',
            cooking_skill='intermediate',
            meals_per_day=3,
            sleep_schedule='flexible'
        )
        profile.set_preferences(['omnivore'])
        profile.set_allergies([])
        profile.set_conditions([])
        profile.set_equipment(['stove', 'oven'])
        
        db.session.add(profile)
        
        # Create settings
        settings = Settings(
            user_id=user.id,
            ollama_url='http://localhost:11434',
            system_prompt='Test system prompt',
            safety_mode=True
        )
        db.session.add(settings)
        db.session.commit()
        
        return user


@pytest.fixture
def logged_in_user(client, auth, user):
    """Create and log in a test user."""
    auth.login()
    return user