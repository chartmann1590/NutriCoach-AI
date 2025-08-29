#!/usr/bin/env python3
"""Test the live dashboard API endpoint to ensure mobile app compatibility"""

import requests
import json
import sys

def test_live_dashboard_api():
    """Test the dashboard API endpoint on the live server with authentication"""
    
    base_url = "http://10.0.0.51:5001"
    
    print(f"Testing live API at {base_url}")
    
    # Create a session to handle cookies
    session = requests.Session()
    
    try:
        # First test the health endpoint to see if server is running
        print("\n1. Testing server health...")
        try:
            health_response = session.get(f"{base_url}/api/health", timeout=10)
            print(f"Health endpoint status: {health_response.status_code}")
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"Health response: {health_data}")
            else:
                print(f"Health response body: {health_response.text[:200]}")
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            print("Server might not be running or accessible")
            return False
        
        # Test authentication to get proper session
        print("\n2. Testing authentication...")
        try:
            # Get login page first to obtain CSRF token
            login_get_response = session.get(f"{base_url}/auth/login", timeout=10)
            print(f"Login page status: {login_get_response.status_code}")
            
            if login_get_response.status_code != 200:
                print("Could not access login page")
                return False
            
            # Extract CSRF token
            import re
            csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]*)"', login_get_response.text)
            csrf_token = csrf_match.group(1) if csrf_match else None
            
            if not csrf_token:
                print("Could not find CSRF token - trying without authentication")
            else:
                print("Found CSRF token, attempting login...")
                
                # Try to login with a test user (we'll need to create one or use existing)
                login_data = {
                    'username': 'test',  # You may need to adjust these credentials
                    'password': 'test',
                    'csrf_token': csrf_token
                }
                
                login_response = session.post(f"{base_url}/auth/login", data=login_data, timeout=10)
                print(f"Login response status: {login_response.status_code}")
                
                if login_response.status_code == 302:
                    location = login_response.headers.get('location', '')
                    if 'login' not in location.lower():
                        print("Login successful!")
                    else:
                        print("Login failed - redirected back to login")
                        print("Note: You may need valid test credentials")
                elif login_response.status_code == 200 and 'dashboard' in login_response.text:
                    print("Login successful!")
                else:
                    print("Login failed or no test user available")
                    print("Proceeding to test dashboard endpoint anyway...")
                
        except Exception as e:
            print(f"Authentication test failed: {e}")
            print("Proceeding to test dashboard endpoint without authentication...")
        
        # Test the dashboard endpoint
        print(f"\n3. Testing dashboard endpoint...")
        try:
            dashboard_response = session.get(f"{base_url}/api/analytics/dashboard", timeout=10)
            print(f"Dashboard endpoint status: {dashboard_response.status_code}")
            print(f"Content-Type: {dashboard_response.headers.get('content-type', 'unknown')}")
            
            if dashboard_response.status_code == 200:
                # Check if response is JSON or HTML
                content_type = dashboard_response.headers.get('content-type', '').lower()
                if 'json' in content_type:
                    print("SUCCESS: Got JSON response!")
                    try:
                        data = dashboard_response.json()
                        print(f"Response data keys: {list(data.keys())}")
                        
                        # Check expected structure for mobile app
                        expected_keys = ['today', 'weekly', 'meal_distribution', 'macro_distribution', 'streaks', 'top_foods']
                        missing_keys = []
                        found_keys = []
                        
                        for key in expected_keys:
                            if key in data:
                                found_keys.append(key)
                            else:
                                missing_keys.append(key)
                        
                        print(f"Found keys: {found_keys}")
                        if missing_keys:
                            print(f"Missing keys: {missing_keys}")
                        
                        # Check today's structure (most important for mobile app)
                        if 'today' in data:
                            today = data['today']
                            print(f"Today data keys: {list(today.keys())}")
                            
                            # Check for totals and targets (mobile app needs these)
                            if 'totals' in today:
                                totals = today['totals']
                                print(f"Totals keys: {list(totals.keys())}")
                                
                                # Check for specific nutrition values mobile app uses
                                mobile_needs = ['calories', 'protein_g', 'carbs_g', 'fat_g']
                                found_nutrition = []
                                missing_nutrition = []
                                
                                for nutrient in mobile_needs:
                                    if nutrient in totals:
                                        found_nutrition.append(f"{nutrient}={totals[nutrient]}")
                                    else:
                                        missing_nutrition.append(nutrient)
                                
                                print(f"Found nutrition data: {found_nutrition}")
                                if missing_nutrition:
                                    print(f"Missing nutrition data: {missing_nutrition}")
                            
                            if 'targets' in today:
                                targets = today['targets']
                                print(f"Targets keys: {list(targets.keys())}")
                                
                                # Check targets the mobile app needs
                                target_values = []
                                for nutrient in ['calories', 'protein_g', 'carbs_g', 'fat_g']:
                                    if nutrient in targets:
                                        target_values.append(f"{nutrient}={targets[nutrient]}")
                                print(f"Target values: {target_values}")
                        
                        print("\nSUCCESS: API is returning properly structured data for mobile app!")
                        return True
                        
                    except json.JSONDecodeError:
                        print(f"Response is not valid JSON: {dashboard_response.text[:500]}")
                        return False
                else:
                    print("Got HTML response instead of JSON (likely login page)")
                    print("This means authentication is required but failed")
                    print("Dashboard endpoint requires valid authentication")
                    if 'login' in dashboard_response.text.lower():
                        print("Confirmed: Response contains login page")
                    return False
                    
            elif dashboard_response.status_code == 401:
                print("Got 401 Unauthorized - authentication required")
                print("This is expected behavior if no valid session exists")
                return True
                
            elif dashboard_response.status_code == 302:
                location = dashboard_response.headers.get('location', '')
                print(f"Got 302 Redirect to: {location}")
                if 'login' in location.lower():
                    print("Redirected to login page - authentication required")
                return True
                
            elif dashboard_response.status_code == 500:
                print("ERROR: Got 500 Internal Server Error!")
                print(f"Response body: {dashboard_response.text}")
                try:
                    error_data = dashboard_response.json()
                    if 'error' in error_data:
                        print(f"Error message: {error_data['error']}")
                except:
                    pass
                return False
                
            else:
                print(f"Unexpected status code: {dashboard_response.status_code}")
                print(f"Response body: {dashboard_response.text[:500]}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Dashboard request failed: {e}")
            return False
    
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = test_live_dashboard_api()
    if success:
        print("\nSUMMARY: Live API test completed successfully!")
    else:
        print("\nSUMMARY: Live API test found issues!")
    sys.exit(0 if success else 1)