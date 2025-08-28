import pytest
from flask import session
from models import User
from extensions import db


class TestAuth:
    
    def test_register_page_loads(self, client):
        """Test registration page loads correctly."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Create your account' in response.data

    def test_login_page_loads(self, client):
        """Test login page loads correctly."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Sign in to your account' in response.data

    def test_register_valid_user(self, client, app):
        """Test user registration with valid data."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'password': 'password123'
        })
        
        # Should redirect to onboarding
        assert response.status_code == 302
        
        # Check user was created
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.check_password('password123')

    def test_register_duplicate_username(self, client, user):
        """Test registration fails with duplicate username."""
        response = client.post('/auth/register', data={
            'username': 'testuser',  # User already exists
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert b'Username already taken' in response.data

    def test_register_invalid_data(self, client):
        """Test registration fails with invalid data."""
        # Short password
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'password': '123'
        })
        assert response.status_code == 200
        assert b'Field must be at least 6 characters long' in response.data

        # Short username
        response = client.post('/auth/register', data={
            'username': 'ab',
            'password': 'password123'
        })
        assert response.status_code == 200
        assert b'Field must be at least 3 characters long' in response.data

    def test_login_valid_user(self, client, user):
        """Test login with valid credentials."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Should redirect to dashboard
        assert response.status_code == 302
        assert '/dashboard' in response.location

    def test_login_invalid_credentials(self, client, user):
        """Test login fails with invalid credentials."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_login_nonexistent_user(self, client):
        """Test login fails with nonexistent user."""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_logout(self, client, auth, user):
        """Test user logout."""
        auth.login()
        
        # Verify user is logged in
        response = client.get('/dashboard')
        assert response.status_code == 200
        
        # Logout
        response = auth.logout()
        assert response.status_code == 302
        
        # Verify user is logged out
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login

    def test_protected_route_requires_auth(self, client):
        """Test protected routes require authentication."""
        protected_routes = [
            '/dashboard',
            '/log',
            '/progress',
            '/settings/',
            '/coach/',
            '/api/logs'
        ]
        
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 302  # Redirect to login

    def test_authenticated_user_redirected_from_auth_pages(self, client, auth, user):
        """Test authenticated users are redirected from auth pages."""
        auth.login()
        
        # Should redirect from login page
        response = client.get('/auth/login')
        assert response.status_code == 302
        
        # Should redirect from register page
        response = client.get('/auth/register')
        assert response.status_code == 302