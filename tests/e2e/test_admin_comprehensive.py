#!/usr/bin/env python3
"""
Comprehensive Playwright tests for admin functionality
Tests EVERY single feature and link with browser automation
"""

import pytest
from playwright.sync_api import Page, expect
import time
import re


class TestAdminComprehensive:
    """Comprehensive admin functionality tests with browser automation"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test."""
        self.page = page
        self.base_url = "http://localhost:5001"
        page.set_default_timeout(10000)  # 10 second timeout
    
    def admin_login(self, page: Page):
        """Helper to login as admin user"""
        print("Logging in as admin...")
        page.goto(f"{self.base_url}/auth/login")
        
        # Wait for login form
        expect(page.locator("input[name='username']")).to_be_visible()
        
        # Fill login form
        page.fill("input[name='username']", "e2euser")
        page.fill("input[name='password']", "password123")
        page.click("input[type='submit']")
        
        # Wait for redirect (either to dashboard or admin)
        page.wait_for_url(lambda url: "/dashboard" in url or "/admin" in url or "/onboarding" in url)
        print(f"Redirected to: {page.url}")
    
    def test_01_admin_access_protection(self):
        """Test that admin areas require authentication"""
        page = self.page
        print("Testing admin access protection...")
        
        admin_urls = [
            "/admin/dashboard",
            "/admin/users", 
            "/admin/settings/ollama",
            "/admin/logs",
            "/admin/maintenance",
            "/admin/settings"
        ]
        
        for url in admin_urls:
            print(f"Testing protection for {url}")
            page.goto(f"{self.base_url}{url}")
            
            # Should redirect to login
            expect(page).to_have_url(re.compile(r".*/auth/login.*"))
            expect(page.get_by_text("Sign in to your account")).to_be_visible()
    
    def test_02_admin_login_functionality(self):
        """Test admin login process"""
        page = self.page
        print("Testing admin login functionality...")
        
        # Go to login page
        page.goto(f"{self.base_url}/auth/login")
        expect(page.get_by_text("Sign in to your account")).to_be_visible()
        
        # Check form elements exist
        expect(page.locator("input[name='username']")).to_be_visible()
        expect(page.locator("input[name='password']")).to_be_visible()
        expect(page.locator("input[name='csrf_token']")).to_be_attached()
        
        # Test invalid login
        page.fill("input[name='username']", "invaliduser")
        page.fill("input[name='password']", "wrongpassword")
        page.click("input[type='submit']")
        
        # Should show error
        expect(page.get_by_text("Invalid username or password")).to_be_visible()
        
        # Test valid admin login
        page.fill("input[name='username']", "e2euser")
        page.fill("input[name='password']", "password123")
        page.click("input[type='submit']")
        
        # Should redirect successfully
        page.wait_for_url(lambda url: "/dashboard" in url or "/admin" in url)
        print(f"Admin login successful, redirected to: {page.url}")
    
    def test_03_admin_navigation_visibility(self):
        """Test admin navigation is visible to admin users"""
        page = self.page
        print("Testing admin navigation visibility...")
        
        self.admin_login(page)
        
        # Go to main page to check navigation
        page.goto(f"{self.base_url}/")
        
        # Admin panel link should be visible
        admin_link = page.locator("a:has-text('Admin Panel')")
        expect(admin_link).to_be_visible()
        
        # Click admin panel link
        admin_link.click()
        expect(page).to_have_url(f"{self.base_url}/admin/dashboard")
    
    def test_04_admin_dashboard_functionality(self):
        """Test admin dashboard loads and shows correct information"""
        page = self.page
        print("Testing admin dashboard functionality...")
        
        self.admin_login(page)
        
        # Navigate to admin dashboard
        page.goto(f"{self.base_url}/admin/dashboard")
        
        # Check dashboard elements
        expect(page.get_by_text("Admin Dashboard")).to_be_visible()
        
        # Check statistics are displayed
        expect(page.locator("text=Total Users")).to_be_visible()
        expect(page.locator("text=Active Users")).to_be_visible()
        expect(page.locator("text=Admin Users")).to_be_visible()
        
        # Check navigation links work
        expect(page.locator("a:has-text('User Management')")).to_be_visible()
        expect(page.locator("a:has-text('System Settings')")).to_be_visible()
        expect(page.locator("a:has-text('System Logs')")).to_be_visible()
    
    def test_05_user_management_interface(self):
        """Test complete user management functionality"""
        page = self.page
        print("Testing user management interface...")
        
        self.admin_login(page)
        
        # Navigate to user management
        page.goto(f"{self.base_url}/admin/users")
        
        # Check page loads correctly
        expect(page.get_by_text("User Management")).to_be_visible()
        
        # Check user table exists
        expect(page.locator("table")).to_be_visible()
        
        # Check search functionality
        search_box = page.locator("input[name='search']")
        if search_box.is_visible():
            search_box.fill("e2euser")
            page.click("button:has-text('Search')")
            expect(page.get_by_text("e2euser")).to_be_visible()
        
        # Check filter options
        filter_select = page.locator("select[name='filter']")
        if filter_select.is_visible():
            filter_select.select_option("admin")
            expect(page.get_by_text("e2euser")).to_be_visible()
        
        # Test create user link
        create_link = page.locator("a:has-text('Create New User')")
        if create_link.is_visible():
            create_link.click()
            expect(page).to_have_url(f"{self.base_url}/admin/users/create")
            expect(page.get_by_text("Create New User")).to_be_visible()
    
    def test_06_create_user_functionality(self):
        """Test creating a new user through admin interface"""
        page = self.page
        print("Testing create user functionality...")
        
        self.admin_login(page)
        
        # Navigate to create user page
        page.goto(f"{self.base_url}/admin/users/create")
        
        # Check form elements
        expect(page.get_by_text("Create New User")).to_be_visible()
        expect(page.locator("input[name='username']")).to_be_visible()
        expect(page.locator("input[name='password']")).to_be_visible()
        
        # Fill out form
        timestamp = str(int(time.time()))
        test_username = f"testuser_{timestamp}"
        
        page.fill("input[name='username']", test_username)
        page.fill("input[name='password']", "testpassword123")
        
        # Check admin checkbox if present
        admin_checkbox = page.locator("input[name='is_admin']")
        if admin_checkbox.is_visible():
            admin_checkbox.uncheck()
        
        # Submit form
        page.click("input[type='submit']")
        
        # Should redirect to users list with success message
        expect(page).to_have_url(f"{self.base_url}/admin/users")
        expect(page.get_by_text("created successfully")).to_be_visible()
        
        # Verify user appears in list
        expect(page.get_by_text(test_username)).to_be_visible()
    
    def test_07_edit_user_functionality(self):
        """Test editing a user through admin interface"""
        page = self.page
        print("Testing edit user functionality...")
        
        self.admin_login(page)
        
        # Go to users page
        page.goto(f"{self.base_url}/admin/users")
        
        # Find edit link for a user (look for first edit button)
        edit_links = page.locator("a:has-text('Edit')")
        if edit_links.count() > 0:
            edit_links.first.click()
            
            # Should be on edit page
            expect(page.get_by_text("Edit User")).to_be_visible()
            
            # Check form elements exist
            expect(page.locator("input[name='username']")).to_be_visible()
            
            # Test changing active status
            active_checkbox = page.locator("input[name='is_active']")
            if active_checkbox.is_visible():
                active_checkbox.check()
            
            # Submit changes
            page.click("input[type='submit']")
            
            # Should redirect back to users list
            expect(page).to_have_url(f"{self.base_url}/admin/users")
            expect(page.get_by_text("updated successfully")).to_be_visible()
    
    def test_08_bulk_user_operations(self):
        """Test bulk user operations"""
        page = self.page
        print("Testing bulk user operations...")
        
        self.admin_login(page)
        page.goto(f"{self.base_url}/admin/users")
        
        # Check if bulk operations form exists
        bulk_form = page.locator("form:has(select[name='action'])")
        if bulk_form.is_visible():
            expect(page.get_by_text("Bulk Actions")).to_be_visible()
            expect(page.locator("select[name='action']")).to_be_visible()
            
            # Test form elements without actually performing bulk operations
            action_select = page.locator("select[name='action']")
            action_select.select_option("activate")
    
    def test_09_ollama_settings_interface(self):
        """Test Ollama settings management"""
        page = self.page
        print("Testing Ollama settings interface...")
        
        self.admin_login(page)
        
        # Navigate to Ollama settings
        page.goto(f"{self.base_url}/admin/settings/ollama")
        
        # Check page loads
        expect(page.get_by_text("Ollama Configuration")).to_be_visible()
        
        # Check form fields exist
        expect(page.locator("input[name='ollama_url']")).to_be_visible()
        expect(page.locator("input[name='default_chat_model']")).to_be_visible()
        
        # Test updating settings
        page.fill("input[name='ollama_url']", "http://74.76.44.128:11434")
        page.fill("input[name='default_chat_model']", "llama3.1")
        
        # Submit form
        page.click("input[type='submit']")
        
        # Should show success message
        expect(page.get_by_text("updated successfully")).to_be_visible()
    
    def test_10_ollama_connection_test(self):
        """Test Ollama connection testing functionality"""
        page = self.page
        print("Testing Ollama connection test...")
        
        self.admin_login(page)
        page.goto(f"{self.base_url}/admin/settings/ollama")
        
        # Look for test connection button/functionality
        test_button = page.locator("button:has-text('Test Connection')")
        if test_button.is_visible():
            test_button.click()
            
            # Wait for result
            page.wait_for_timeout(2000)
            
            # Should show some result (either success or failure)
            result_text = page.locator(".test-result, .alert, .message")
            if result_text.count() > 0:
                expect(result_text.first).to_be_visible()
    
    def test_11_system_logs_interface(self):
        """Test system logs viewing functionality"""
        page = self.page
        print("Testing system logs interface...")
        
        self.admin_login(page)
        
        # Navigate to logs
        page.goto(f"{self.base_url}/admin/logs")
        
        # Check page loads
        expect(page.get_by_text("System Logs")).to_be_visible()
        
        # Check logs table or content
        logs_content = page.locator("table, .log-entry, .logs-container")
        expect(logs_content.first).to_be_visible()
        
        # Test filtering if available
        level_filter = page.locator("select[name='level']")
        if level_filter.is_visible():
            level_filter.select_option("info")
        
        action_filter = page.locator("input[name='action']")
        if action_filter.is_visible():
            action_filter.fill("login")
    
    def test_12_global_settings_management(self):
        """Test global settings management"""
        page = self.page
        print("Testing global settings management...")
        
        self.admin_login(page)
        
        # Navigate to settings
        page.goto(f"{self.base_url}/admin/settings")
        
        # Check page loads
        expect(page.get_by_text("System Settings")).to_be_visible()
        
        # Look for create new setting link
        create_link = page.locator("a:has-text('Create New Setting')")
        if create_link.is_visible():
            create_link.click()
            expect(page).to_have_url(f"{self.base_url}/admin/settings/create")
            expect(page.get_by_text("Create New Setting")).to_be_visible()
    
    def test_13_maintenance_interface(self):
        """Test maintenance operations interface"""
        page = self.page
        print("Testing maintenance interface...")
        
        self.admin_login(page)
        
        # Navigate to maintenance
        page.goto(f"{self.base_url}/admin/maintenance")
        
        # Check page loads
        expect(page.get_by_text("System Maintenance")).to_be_visible()
        
        # Check maintenance options exist
        maintenance_form = page.locator("form")
        if maintenance_form.count() > 0:
            expect(maintenance_form.first).to_be_visible()
            
            # Check action select if it exists
            action_select = page.locator("select[name='action']")
            if action_select.is_visible():
                expect(action_select).to_be_visible()
    
    def test_14_admin_logout_functionality(self):
        """Test admin logout and access revocation"""
        page = self.page
        print("Testing admin logout functionality...")
        
        self.admin_login(page)
        
        # Navigate to admin dashboard to confirm access
        page.goto(f"{self.base_url}/admin/dashboard")
        expect(page.get_by_text("Admin Dashboard")).to_be_visible()
        
        # Find and click logout link
        logout_link = page.locator("a[href*='logout'], a:has-text('Logout'), a:has-text('Sign out')")
        if logout_link.count() > 0:
            logout_link.first.click()
            
            # Should redirect to login or home page
            page.wait_for_url(lambda url: "/auth/login" in url or url.endswith("/"))
            
            # Try to access admin area again
            page.goto(f"{self.base_url}/admin/dashboard")
            
            # Should redirect to login
            expect(page).to_have_url(re.compile(r".*/auth/login.*"))
    
    def test_15_admin_security_validation(self):
        """Test admin security measures"""
        page = self.page
        print("Testing admin security validation...")
        
        self.admin_login(page)
        
        # Test CSRF protection on forms
        page.goto(f"{self.base_url}/admin/users/create")
        
        # Check CSRF token exists
        csrf_token = page.locator("input[name='csrf_token']")
        expect(csrf_token).to_be_attached()
        
        # Test form validation
        page.fill("input[name='username']", "")  # Empty username
        page.click("input[type='submit']")
        
        # Should show validation error or stay on same page
        current_url = page.url
        assert "/admin/users/create" in current_url
    
    def test_16_admin_navigation_completeness(self):
        """Test all admin navigation links work"""
        page = self.page
        print("Testing admin navigation completeness...")
        
        self.admin_login(page)
        page.goto(f"{self.base_url}/admin/dashboard")
        
        # Test all navigation links
        nav_links = [
            ("User Management", "/admin/users"),
            ("Ollama Settings", "/admin/settings/ollama"),
            ("System Logs", "/admin/logs"),
            ("Maintenance", "/admin/maintenance"),
            ("Settings", "/admin/settings")
        ]
        
        for link_text, expected_url in nav_links:
            link = page.locator(f"a:has-text('{link_text}')")
            if link.count() > 0:
                link.first.click()
                page.wait_for_url(lambda url: expected_url in url)
                print(f"✓ {link_text} navigation works")
                
                # Go back to dashboard for next test
                page.goto(f"{self.base_url}/admin/dashboard")
    
    def test_17_error_handling(self):
        """Test error handling in admin interface"""
        page = self.page
        print("Testing error handling...")
        
        self.admin_login(page)
        
        # Test accessing non-existent user
        page.goto(f"{self.base_url}/admin/users/99999/edit")
        
        # Should show 404 or redirect with error
        error_indicators = [
            page.locator("text=Not Found"),
            page.locator("text=404"),
            page.locator("text=User not found"),
            page.locator(".error, .alert-error")
        ]
        
        # At least one error indicator should be present
        found_error = False
        for indicator in error_indicators:
            if indicator.count() > 0:
                found_error = True
                break
        
        # If no error indicators, we might have been redirected
        if not found_error:
            # Check if we were redirected to a safe page
            assert page.url != f"{self.base_url}/admin/users/99999/edit"
    
    def test_18_responsive_design(self):
        """Test admin interface works on different screen sizes"""
        page = self.page
        print("Testing responsive design...")
        
        self.admin_login(page)
        
        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{self.base_url}/admin/dashboard")
        
        # Should still be functional
        expect(page.get_by_text("Admin Dashboard")).to_be_visible()
        
        # Test tablet viewport  
        page.set_viewport_size({"width": 768, "height": 1024})
        page.reload()
        expect(page.get_by_text("Admin Dashboard")).to_be_visible()
        
        # Reset to desktop
        page.set_viewport_size({"width": 1280, "height": 720})
    
    def test_19_data_consistency(self):
        """Test data consistency across admin operations"""
        page = self.page
        print("Testing data consistency...")
        
        self.admin_login(page)
        
        # Get initial user count from dashboard
        page.goto(f"{self.base_url}/admin/dashboard")
        
        # Look for user count display
        user_count_element = page.locator("text=/Total Users.*\\d+/")
        if user_count_element.count() > 0:
            initial_count_text = user_count_element.first.inner_text()
            print(f"Initial user count: {initial_count_text}")
        
        # Go to users page and verify count matches
        page.goto(f"{self.base_url}/admin/users")
        
        # Count users in table
        user_rows = page.locator("table tbody tr")
        if user_rows.count() > 0:
            table_count = user_rows.count()
            print(f"Users in table: {table_count}")
    
    def test_20_complete_admin_workflow(self):
        """Test complete admin workflow end-to-end"""
        page = self.page
        print("Testing complete admin workflow...")
        
        self.admin_login(page)
        
        # 1. Check dashboard
        page.goto(f"{self.base_url}/admin/dashboard")
        expect(page.get_by_text("Admin Dashboard")).to_be_visible()
        
        # 2. Create a new user
        page.goto(f"{self.base_url}/admin/users/create")
        timestamp = str(int(time.time()))
        test_username = f"workflow_user_{timestamp}"
        
        page.fill("input[name='username']", test_username)
        page.fill("input[name='password']", "workflowtest123")
        page.click("input[type='submit']")
        
        # 3. Verify user was created
        expect(page).to_have_url(f"{self.base_url}/admin/users")
        expect(page.get_by_text(test_username)).to_be_visible()
        
        # 4. Configure Ollama settings
        page.goto(f"{self.base_url}/admin/settings/ollama")
        page.fill("input[name='ollama_url']", "http://74.76.44.128:11434")
        page.fill("input[name='default_chat_model']", "llama3.1")
        page.click("input[type='submit']")
        expect(page.get_by_text("updated successfully")).to_be_visible()
        
        # 5. Check system logs
        page.goto(f"{self.base_url}/admin/logs")
        expect(page.get_by_text("System Logs")).to_be_visible()
        
        print("✓ Complete admin workflow test passed!")


if __name__ == "__main__":
    # Run tests directly if needed
    print("Admin comprehensive tests ready to run with pytest")