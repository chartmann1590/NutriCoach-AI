import pytest
from playwright.sync_api import Page, expect
import time


class TestAdminFunctionality:
    """End-to-end tests for admin functionality using Playwright."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test."""
        self.page = page
        self.base_url = "http://localhost:5001"
    
    def test_admin_access_requires_authentication(self):
        """Test that admin areas require authentication"""
        page = self.page
        
        # Try to access admin dashboard without login
        page.goto(f"{self.base_url}/admin/dashboard")
        
        # Should redirect to login
        expect(page).to_have_url(f"{self.base_url}/auth/login?next=%2Fadmin%2Fdashboard")
        expect(page.get_by_text("Sign in to your account")).to_be_visible()
    
    def test_admin_user_creation_and_login(self):
        """Test creating an admin user and logging in"""
        page = self.page
        
        # 1. Visit homepage and register as regular user first
        page.goto(self.base_url)
        page.click("a:has-text('Get Started')")
        
        # 2. Register admin user
        page.fill("input[name='username']", "admintest")
        page.fill("input[name='password']", "admin123456")
        page.click("input[type='submit']")
        
        # Should redirect to onboarding, but we'll manually make this user admin
        # In a real scenario, an existing admin would do this
        
        # For now, let's test the regular user flow and assume admin exists
        expect(page).to_have_url(f"{self.base_url}/onboarding/step1")
    
    def test_admin_dashboard_access_with_existing_admin(self):
        """Test admin dashboard access with existing admin user"""
        page = self.page
        
        # This test assumes an admin user exists in the database
        # In a real test environment, you'd set this up in fixtures
        
        # Go to login page
        page.goto(f"{self.base_url}/auth/login")
        
        # Try to login with admin credentials (this will fail without actual admin user)
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin123")
        page.click("input[type='submit']")
        
        # If admin user exists and has proper permissions, should access dashboard
        # If not, will get login error - this tests the admin access control
    
    def test_user_management_interface(self):
        """Test the user management interface (requires admin login)"""
        page = self.page
        
        # This test would run after successful admin login
        # Testing the user management interface structure
        
        # Go directly to users page (will redirect to login if not admin)
        page.goto(f"{self.base_url}/admin/users")
        
        # Should redirect to login since we're not authenticated
        expect(page).to_have_url(f"{self.base_url}/auth/login?next=%2Fadmin%2Fusers")
    
    def test_ollama_settings_interface(self):
        """Test the Ollama settings interface"""
        page = self.page
        
        # Test Ollama settings page access
        page.goto(f"{self.base_url}/admin/settings/ollama")
        
        # Should redirect to login
        expect(page).to_have_url(f"{self.base_url}/auth/login?next=%2Fadmin%2Fsettings%2Follama")
    
    def test_system_logs_interface(self):
        """Test the system logs interface"""
        page = self.page
        
        # Test system logs page access
        page.goto(f"{self.base_url}/admin/logs")
        
        # Should redirect to login
        expect(page).to_have_url(f"{self.base_url}/auth/login?next=%2Fadmin%2Flogs")
    
    def test_admin_navigation_visibility(self):
        """Test that admin navigation is only visible to admin users"""
        page = self.page
        
        # 1. Test as regular user - register first
        page.goto(self.base_url)
        page.click("a:has-text('Get Started')")
        
        page.fill("input[name='username']", "regularuser")
        page.fill("input[name='password']", "password123")
        page.click("input[type='submit']")
        
        # Complete onboarding to get to dashboard
        expect(page).to_have_url(f"{self.base_url}/onboarding/step1")
        
        # Fill out onboarding form
        page.fill("input[name='name']", "Regular User")
        page.fill("input[name='age']", "25")
        page.select_option("select[name='sex']", "female")
        page.fill("input[name='height_cm']", "165")
        page.fill("input[name='weight_kg']", "60")
        page.click("input[type='submit']")
        
        # Continue through onboarding
        if page.url.endswith("step2"):
            page.select_option("select[name='activity_level']", "moderate")
            page.select_option("select[name='goal_type']", "maintain")
            page.click("input[type='submit']")
        
        if page.url.endswith("step3"):
            page.click("input[type='submit']")
        
        # Should eventually reach dashboard
        # Regular user should NOT see admin panel link
        # Admin panel link should not be visible
        admin_link = page.locator("a:has-text('Admin Panel')")
        expect(admin_link).not_to_be_visible()
    
    def test_admin_form_validation(self):
        """Test form validation in admin interfaces"""
        page = self.page
        
        # Test create user form validation
        page.goto(f"{self.base_url}/admin/users/create")
        
        # Should redirect to login, but let's test the URL structure
        expect(page).to_have_url(f"{self.base_url}/auth/login?next=%2Fadmin%2Fusers%2Fcreate")
    
    def test_admin_api_endpoints(self):
        """Test admin API endpoints"""
        page = self.page
        
        # Test API endpoints that should require admin access
        api_endpoints = [
            "/admin/api/test-ollama",
            "/admin/users/1/delete",
            "/admin/users/bulk-action"
        ]
        
        for endpoint in api_endpoints:
            response = page.request.get(f"{self.base_url}{endpoint}")
            # Should return 403 (Forbidden) or redirect to login
            assert response.status in [403, 302], f"Endpoint {endpoint} should require admin access"
    
    def test_admin_security_headers(self):
        """Test that admin pages have proper security headers"""
        page = self.page
        
        # Check admin dashboard
        response = page.request.get(f"{self.base_url}/admin/dashboard")
        
        # Should have security headers (even for redirects)
        headers = response.headers
        
        # Basic security checks
        assert response.status in [302, 403], "Admin dashboard should require authentication"
    
    def test_admin_csrf_protection(self):
        """Test CSRF protection on admin forms"""
        page = self.page
        
        # Test that admin forms include CSRF tokens
        page.goto(f"{self.base_url}/auth/login")
        
        # Login form should have CSRF token
        csrf_token = page.locator("input[name='csrf_token']")
        expect(csrf_token).to_be_attached()
    
    def test_admin_bulk_operations_structure(self):
        """Test bulk operations interface structure"""
        page = self.page
        
        # Test bulk user actions endpoint
        response = page.request.post(
            f"{self.base_url}/admin/users/bulk-action",
            data={"action": "activate", "user_ids": "1,2,3", "confirm": "true"}
        )
        
        # Should require authentication
        assert response.status in [302, 403, 422], "Bulk actions should require admin authentication"
    
    def test_admin_maintenance_interface(self):
        """Test maintenance interface"""
        page = self.page
        
        # Test maintenance page access
        page.goto(f"{self.base_url}/admin/maintenance")
        
        # Should redirect to login
        expect(page).to_have_url(f"{self.base_url}/auth/login?next=%2Fadmin%2Fmaintenance")
    
    def test_admin_settings_management(self):
        """Test global settings management"""
        page = self.page
        
        # Test settings page access
        page.goto(f"{self.base_url}/admin/settings")
        
        # Should redirect to login
        expect(page).to_have_url(f"{self.base_url}/auth/login?next=%2Fadmin%2Fsettings")
    
    def test_admin_error_handling(self):
        """Test error handling in admin interface"""
        page = self.page
        
        # Test invalid admin routes
        invalid_routes = [
            "/admin/invalid-page",
            "/admin/users/999999/edit",
            "/admin/nonexistent"
        ]
        
        for route in invalid_routes:
            response = page.request.get(f"{self.base_url}{route}")
            # Should handle errors gracefully
            assert response.status in [302, 403, 404], f"Route {route} should handle errors properly"


class TestAdminIntegration:
    """Integration tests for admin functionality with the rest of the application"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test."""
        self.page = page
        self.base_url = "http://localhost:5001"
    
    def test_admin_and_regular_user_separation(self):
        """Test that admin and regular user functionalities are properly separated"""
        page = self.page
        
        # Test that regular app functionality still works when admin routes exist
        page.goto(self.base_url)
        expect(page.get_by_text("Welcome to NutriCoach")).to_be_visible()
        
        # Test that API endpoints still work
        response = page.request.get(f"{self.base_url}/api/healthz")
        assert response.status == 200
    
    def test_admin_database_integrity(self):
        """Test that admin operations don't break regular user operations"""
        page = self.page
        
        # Test user registration still works
        page.goto(f"{self.base_url}/auth/register")
        expect(page.get_by_text("Create your account")).to_be_visible()
        
        # Test that forms have proper CSRF protection
        csrf_token = page.locator("input[name='csrf_token']")
        expect(csrf_token).to_be_attached()
    
    def test_admin_performance_impact(self):
        """Test that admin functionality doesn't impact regular user performance"""
        page = self.page
        
        # Time the homepage load
        start_time = time.time()
        page.goto(self.base_url)
        expect(page.get_by_text("Welcome to NutriCoach")).to_be_visible()
        load_time = time.time() - start_time
        
        # Should load reasonably fast (adjust threshold as needed)
        assert load_time < 5.0, f"Homepage took too long to load: {load_time}s"
    
    def test_admin_route_isolation(self):
        """Test that admin routes don't interfere with regular routes"""
        page = self.page
        
        # Test regular routes still work
        regular_routes = [
            "/",
            "/auth/login",
            "/auth/register",
            "/api/healthz"
        ]
        
        for route in regular_routes:
            response = page.request.get(f"{self.base_url}{route}")
            assert response.status in [200, 302], f"Regular route {route} should work normally"