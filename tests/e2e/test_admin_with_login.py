import pytest
from playwright.sync_api import Page, expect
import time


class TestAdminWithLogin:
    """E2E tests for admin functionality with actual admin login"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test."""
        self.page = page
        self.base_url = "http://localhost:5001"
    
    def login_as_admin(self, page):
        """Helper to login as admin user"""
        page.goto(f"{self.base_url}/auth/login")
        page.fill("input[name='username']", "e2euser")  # This user was made admin
        page.fill("input[name='password']", "password123")
        page.click("input[type='submit']")
        
        # Should redirect after successful login
        # If user has no profile, goes to onboarding
        # If user has profile, goes to dashboard
        
    def test_admin_dashboard_access(self):
        """Test accessing admin dashboard with admin user"""
        page = self.page
        
        # Login as admin
        self.login_as_admin(page)
        
        # Navigate to admin dashboard
        page.goto(f"{self.base_url}/admin/dashboard")
        
        # Should be able to access admin dashboard
        expect(page.get_by_text("Admin Dashboard")).to_be_visible()
        
    def test_admin_navigation_visible(self):
        """Test that admin navigation is visible to admin users"""
        page = self.page
        
        # Login as admin
        self.login_as_admin(page)
        
        # Go to main dashboard
        page.goto(f"{self.base_url}/")
        
        # Should see admin panel link in navigation
        admin_link = page.locator("a:has-text('Admin Panel')")
        expect(admin_link).to_be_visible()
        
    def test_admin_user_management(self):
        """Test admin user management functionality"""
        page = self.page
        
        # Login as admin
        self.login_as_admin(page)
        
        # Navigate to user management
        page.goto(f"{self.base_url}/admin/users")
        
        # Should see user management interface
        expect(page.get_by_text("User Management")).to_be_visible()
        
        # Should see existing users in table
        expect(page.locator("table")).to_be_visible()
        
    def test_admin_create_user(self):
        """Test creating a new user via admin interface"""
        page = self.page
        
        # Login as admin
        self.login_as_admin(page)
        
        # Navigate to create user
        page.goto(f"{self.base_url}/admin/users/create")
        
        # Should see create user form
        expect(page.get_by_text("Create New User")).to_be_visible()
        
        # Fill out form
        page.fill("input[name='username']", f"testuser_{int(time.time())}")
        page.fill("input[name='password']", "password123")
        
        # Submit form
        page.click("input[type='submit']")
        
        # Should redirect to users list
        expect(page).to_have_url(f"{self.base_url}/admin/users")
        expect(page.get_by_text("created successfully")).to_be_visible()
        
    def test_admin_ollama_settings(self):
        """Test Ollama settings management"""
        page = self.page
        
        # Login as admin
        self.login_as_admin(page)
        
        # Navigate to Ollama settings
        page.goto(f"{self.base_url}/admin/settings/ollama")
        
        # Should see Ollama configuration
        expect(page.get_by_text("Ollama Configuration")).to_be_visible()
        
        # Should see form fields
        expect(page.locator("input[name='ollama_url']")).to_be_visible()
        expect(page.locator("input[name='default_chat_model']")).to_be_visible()
        
    def test_admin_system_logs(self):
        """Test system logs viewing"""
        page = self.page
        
        # Login as admin
        self.login_as_admin(page)
        
        # Navigate to system logs
        page.goto(f"{self.base_url}/admin/logs")
        
        # Should see logs interface
        expect(page.get_by_text("System Logs")).to_be_visible()
        
    def test_admin_settings_update(self):
        """Test updating system settings"""
        page = self.page
        
        # Login as admin
        self.login_as_admin(page)
        
        # Navigate to Ollama settings
        page.goto(f"{self.base_url}/admin/settings/ollama")
        
        # Update a setting
        page.fill("input[name='ollama_url']", "http://test-ollama:11434")
        page.click("input[type='submit']")
        
        # Should show success message
        expect(page.get_by_text("updated successfully")).to_be_visible()
        
    def test_admin_api_access(self):
        """Test admin API endpoint access"""
        page = self.page
        
        # Login as admin first
        self.login_as_admin(page)
        
        # Test API endpoint with proper authentication
        # This would require proper session handling in the test
        # For now, just test that the endpoints exist and have proper structure
        
        response = page.request.get(f"{self.base_url}/admin/dashboard")
        assert response.status == 200, "Admin dashboard should be accessible to admin users"
        
    def test_admin_logout_and_access_denied(self):
        """Test that after logout, admin areas are no longer accessible"""
        page = self.page
        
        # Login as admin
        self.login_as_admin(page)
        
        # Verify admin access works
        page.goto(f"{self.base_url}/admin/dashboard")
        expect(page.get_by_text("Admin Dashboard")).to_be_visible()
        
        # Logout
        page.click("a[href*='logout']")
        
        # Try to access admin area
        page.goto(f"{self.base_url}/admin/dashboard")
        
        # Should redirect to login
        expect(page).to_have_url(f"{self.base_url}/auth/login?next=%2Fadmin%2Fdashboard")
        
    def test_admin_bulk_user_operations(self):
        """Test bulk user operations"""
        page = self.page
        
        # Login as admin
        self.login_as_admin(page)
        
        # Navigate to users
        page.goto(f"{self.base_url}/admin/users")
        
        # Test bulk operations form exists
        expect(page.get_by_text("Bulk Actions")).to_be_visible()
        expect(page.locator("select[name='action']")).to_be_visible()
        
    def test_admin_maintenance_functions(self):
        """Test maintenance functions"""
        page = self.page
        
        # Login as admin
        self.login_as_admin(page)
        
        # Navigate to maintenance
        page.goto(f"{self.base_url}/admin/maintenance")
        
        # Should see maintenance interface
        expect(page.get_by_text("System Maintenance")).to_be_visible() or expect(page.get_by_text("Maintenance")).to_be_visible()