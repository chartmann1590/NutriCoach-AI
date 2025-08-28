import pytest
from playwright.sync_api import Page, expect
import time


class TestUserJourney:
    """End-to-end tests for complete user journeys using Playwright."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test."""
        self.page = page
        # Assume the app is running on localhost:5001
        self.base_url = "http://localhost:5001"
    
    def test_complete_user_onboarding_flow(self):
        """Test complete user registration and onboarding flow."""
        page = self.page
        
        # 1. Visit homepage
        page.goto(self.base_url)
        expect(page.locator("h1")).to_contain_text("Welcome to NutriCoach")
        
        # 2. Click "Get Started" button
        page.click("a:has-text('Get Started')")
        expect(page).to_have_url(f"{self.base_url}/auth/register")
        
        # 3. Register new user
        page.fill("input[name='username']", "e2euser")
        page.fill("input[name='password']", "password123")
        page.click("input[type='submit']")
        
        # Should redirect to onboarding step 1
        expect(page).to_have_url(f"{self.base_url}/onboarding/step1")
        expect(page.get_by_role("heading", name="Basic Information")).to_be_visible()
        
        # 4. Fill out step 1 - Basic Information
        page.fill("input[name='name']", "E2E Test User")
        page.fill("input[name='age']", "28")
        page.select_option("select[name='sex']", "male")
        page.fill("input[name='height_cm']", "180")
        page.fill("input[name='weight_kg']", "75")
        page.click("button[type='submit']")
        
        # Should redirect to step 2
        expect(page).to_have_url(f"{self.base_url}/onboarding/step2")
        expect(page.locator("h3")).to_contain_text("Goals")
        
        # 5. Fill out step 2 - Goals
        page.select_option("select[name='activity_level']", "moderate")
        page.select_option("select[name='goal_type']", "lose")
        page.fill("input[name='target_weight_kg']", "70")
        page.fill("input[name='timeframe_weeks']", "12")
        page.click("button[type='submit']")
        
        # Should redirect to step 3
        expect(page).to_have_url(f"{self.base_url}/onboarding/step3")
        expect(page.locator("h3")).to_contain_text("Lifestyle")
        
        # 6. Fill out step 3 - Lifestyle
        page.check("input[value='omnivore']")
        page.check("input[value='nuts']")  # Allergy
        page.select_option("select[name='budget_range']", "medium")
        page.select_option("select[name='cooking_skill']", "intermediate")
        page.check("input[value='stove']")
        page.check("input[value='oven']")
        page.select_option("select[name='meals_per_day']", "3")
        page.select_option("select[name='sleep_schedule']", "flexible")
        page.click("button[type='submit']")
        
        # Should redirect to step 4
        expect(page).to_have_url(f"{self.base_url}/onboarding/step4")
        expect(page.locator("h3")).to_contain_text("Ollama Settings")
        
        # 7. Complete step 4 - Ollama Settings (skip model setup for e2e)
        page.fill("input[name='ollama_url']", "http://localhost:11434")
        page.click("button[type='submit']")
        
        # Should redirect to dashboard
        expect(page).to_have_url(f"{self.base_url}/dashboard")
        expect(page.locator("h3")).to_contain_text("Welcome back, E2E Test User!")
    
    def test_food_logging_workflow(self):
        """Test complete food logging workflow."""
        page = self.page
        
        # Login first
        self._login_user(page)
        
        # Navigate to food logging
        page.click("a:has-text('Log Food')")
        expect(page).to_have_url(f"{self.base_url}/log")
        
        # Fill out food log form
        page.fill("input[name='custom_name']", "Grilled Chicken Breast")
        page.select_option("select[name='meal']", "lunch")
        page.fill("input[name='grams']", "150")
        page.fill("input[name='calories']", "231")
        page.fill("input[name='protein_g']", "43.5")
        page.fill("input[name='carbs_g']", "0")
        page.fill("input[name='fat_g']", "5")
        
        # Submit the form
        page.click("button[type='submit']")
        
        # Should show success message
        expect(page.locator(".toast")).to_contain_text("logged successfully")
        
        # Navigate back to dashboard and verify the food appears
        page.click("a:has-text('Dashboard')")
        expect(page.locator("text=Grilled Chicken Breast")).to_be_visible()
    
    def test_nutrition_search_workflow(self):
        """Test nutrition search functionality."""
        page = self.page
        
        # Login first
        self._login_user(page)
        
        # Navigate to search page
        page.click("a:has-text('Food Search')")
        expect(page).to_have_url(f"{self.base_url}/search")
        
        # Perform a search
        page.fill("input[placeholder*='Search']", "apple")
        page.click("button:has-text('Search')")
        
        # Wait for results to load
        page.wait_for_selector(".search-results", timeout=5000)
        
        # Verify search results appear
        expect(page.locator(".search-results")).to_be_visible()
    
    def test_settings_update_workflow(self):
        """Test updating user settings."""
        page = self.page
        
        # Login first
        self._login_user(page)
        
        # Navigate to settings
        page.click("a:has-text('Settings')")
        expect(page).to_have_url(f"{self.base_url}/settings/")
        
        # Navigate to profile settings
        page.click("a:has-text('Profile')")
        expect(page).to_have_url(f"{self.base_url}/settings/profile")
        
        # Update profile information
        page.fill("input[name='name']", "Updated Test User")
        page.fill("input[name='age']", "29")
        page.click("button[type='submit']")
        
        # Should show success message
        expect(page.locator(".toast")).to_contain_text("updated successfully")
        
        # Verify changes are reflected
        expect(page.locator("input[name='name']")).to_have_value("Updated Test User")
    
    def test_ai_coach_interaction(self):
        """Test AI coach chat interface."""
        page = self.page
        
        # Login first
        self._login_user(page)
        
        # Navigate to AI coach
        page.click("a:has-text('AI Coach')")
        expect(page).to_have_url(f"{self.base_url}/coach/")
        
        # Type a message
        page.fill("textarea[placeholder*='message']", "What should I eat for breakfast?")
        page.click("button:has-text('Send')")
        
        # Should see the message in chat history
        expect(page.locator(".chat-message")).to_contain_text("What should I eat for breakfast?")
    
    def test_progress_analytics_view(self):
        """Test progress and analytics page."""
        page = self.page
        
        # Login first
        self._login_user(page)
        
        # Navigate to progress page
        page.click("a:has-text('Progress')")
        expect(page).to_have_url(f"{self.base_url}/progress")
        
        # Verify analytics components are present
        expect(page.locator("h3:has-text('Progress')")).to_be_visible()
        
        # Check for chart containers (even if no data)
        expect(page.locator("canvas")).to_be_visible()
    
    def test_mobile_responsiveness(self):
        """Test mobile responsiveness."""
        page = self.page
        
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        
        # Login
        self._login_user(page)
        
        # Mobile menu should be visible
        page.click("button[aria-label*='menu']")
        
        # Navigation should be accessible
        expect(page.locator("nav")).to_be_visible()
        
        # Test navigation works on mobile
        page.click("a:has-text('Dashboard')")
        expect(page).to_have_url(f"{self.base_url}/dashboard")
    
    def test_dark_mode_toggle(self):
        """Test dark mode functionality."""
        page = self.page
        
        # Login first
        self._login_user(page)
        
        # Toggle dark mode
        page.click("button[title*='dark']")
        
        # Verify dark mode is applied
        expect(page.locator("html")).to_have_class("dark")
        
        # Toggle back to light mode
        page.click("button[title*='light']")
        
        # Verify light mode is restored
        expect(page.locator("html")).not_to_have_class("dark")
    
    def test_photo_upload_interface(self):
        """Test photo upload interface."""
        page = self.page
        
        # Login first
        self._login_user(page)
        
        # Navigate to photo upload
        page.click("a:has-text('Photo Log')")
        expect(page).to_have_url(f"{self.base_url}/photo-upload")
        
        # Verify upload interface is present
        expect(page.locator("input[type='file']")).to_be_visible()
        expect(page.locator("button:has-text('Upload')")).to_be_visible()
    
    def test_quick_log_modal(self):
        """Test quick log modal functionality."""
        page = self.page
        
        # Login first
        self._login_user(page)
        
        # Click quick log button (plus icon in top bar)
        page.click("button:has-text('+')")
        
        # Verify modal appears
        expect(page.locator("#quick-log-modal")).to_be_visible()
        
        # Test water logging
        page.select_option("select[name='ml']", "500")
        page.click("button:has-text('Log Water')")
        
        # Should show success response
        expect(page.locator("#quick-log-response")).to_contain_text("success")
    
    def _login_user(self, page: Page):
        """Helper method to login a test user."""
        # Go to login page
        page.goto(f"{self.base_url}/auth/login")
        
        # Create account if needed (for isolation)
        try:
            page.click("a:has-text('create a new account')")
            page.fill("input[name='username']", "testuser")
            page.fill("input[name='password']", "password123")
            page.click("button[type='submit']")
            
            # Skip onboarding
            page.click("a:has-text('Skip Setup')")
        except:
            # User might already exist, try to login
            page.goto(f"{self.base_url}/auth/login")
            page.fill("input[name='username']", "testuser")
            page.fill("input[name='password']", "password123")
            page.click("button[type='submit']")
        
        # Verify we're logged in
        expect(page).to_have_url(f"{self.base_url}/dashboard")


class TestAccessibility:
    """Test accessibility features."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test."""
        self.page = page
        self.base_url = "http://localhost:5000"
    
    def test_keyboard_navigation(self):
        """Test keyboard navigation works properly."""
        page = self.page
        page.goto(self.base_url)
        
        # Test tab navigation
        page.keyboard.press("Tab")
        expect(page.locator(":focus")).to_be_visible()
        
        # Continue tabbing through focusable elements
        for _ in range(5):
            page.keyboard.press("Tab")
            expect(page.locator(":focus")).to_be_visible()
    
    def test_aria_labels_present(self):
        """Test that important elements have proper ARIA labels."""
        page = self.page
        page.goto(self.base_url)
        
        # Check for proper labeling on interactive elements
        buttons = page.locator("button")
        for i in range(buttons.count()):
            button = buttons.nth(i)
            # Button should have either text content or aria-label
            text = button.text_content()
            aria_label = button.get_attribute("aria-label")
            assert text or aria_label, f"Button {i} missing accessible text"
    
    def test_color_contrast(self):
        """Test that text has sufficient color contrast."""
        page = self.page
        page.goto(self.base_url)
        
        # This is a basic check - in production you'd use axe-core
        # Check that text is visible against backgrounds
        text_elements = page.locator("p, h1, h2, h3, h4, h5, h6, span")
        for i in range(min(10, text_elements.count())):  # Check first 10
            element = text_elements.nth(i)
            expect(element).to_be_visible()


class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test."""
        self.page = page
        self.base_url = "http://localhost:5000"
    
    def test_page_load_times(self):
        """Test that pages load within acceptable time limits."""
        page = self.page
        
        # Test homepage load time
        start_time = time.time()
        page.goto(self.base_url)
        load_time = time.time() - start_time
        
        assert load_time < 5.0, f"Homepage took {load_time}s to load (should be < 5s)"
        
        # Test that page is interactive
        expect(page.locator("a:has-text('Get Started')")).to_be_visible()
    
    def test_large_dataset_handling(self):
        """Test app handles larger datasets appropriately."""
        page = self.page
        
        # This would test pagination, infinite scroll, etc.
        # For now, just ensure pages don't crash with existing data
        page.goto(f"{self.base_url}/auth/login")
        
        # Login and check that dashboard loads with any existing data
        page.fill("input[name='username']", "testuser")
        page.fill("input[name='password']", "password123")
        page.click("button[type='submit']")
        
        # Dashboard should load regardless of data volume
        expect(page.locator("h3")).to_contain_text("Welcome")


class TestSecurity:
    """Test security features."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test."""
        self.page = page
        self.base_url = "http://localhost:5000"
    
    def test_unauthenticated_access_blocked(self):
        """Test that protected routes require authentication."""
        page = self.page
        
        protected_urls = [
            "/dashboard",
            "/settings/",
            "/coach/",
            "/progress",
            "/log"
        ]
        
        for url in protected_urls:
            page.goto(f"{self.base_url}{url}")
            # Should redirect to login
            expect(page).to_have_url(f"{self.base_url}/auth/login")
    
    def test_csrf_protection(self):
        """Test that forms include CSRF protection."""
        page = self.page
        page.goto(f"{self.base_url}/auth/register")
        
        # Check that forms have CSRF tokens
        csrf_token = page.locator("input[name='csrf_token']")
        expect(csrf_token).to_be_attached()
        expect(csrf_token.get_attribute("value")).not_to_be_empty()
    
    def test_session_management(self):
        """Test proper session handling."""
        page = self.page
        
        # Login
        page.goto(f"{self.base_url}/auth/login")
        page.fill("input[name='username']", "testuser")
        page.fill("input[name='password']", "password123")
        page.click("button[type='submit']")
        
        # Should be logged in
        expect(page).to_have_url(f"{self.base_url}/dashboard")
        
        # Logout
        page.click("a[href='/auth/logout']")
        
        # Should be logged out and redirected
        expect(page).to_have_url(f"{self.base_url}/auth/login")
        
        # Try to access protected page - should be denied
        page.goto(f"{self.base_url}/dashboard")
        expect(page).to_have_url(f"{self.base_url}/auth/login")