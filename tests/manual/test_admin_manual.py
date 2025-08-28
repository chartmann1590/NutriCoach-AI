#!/usr/bin/env python3
"""
Manual test script for admin functionality
"""

import requests
import time

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

def test_admin_login():
    """Test admin login functionality"""
    print("Testing admin login...")
    
    # Get login page
    response = session.get(f"{BASE_URL}/auth/login")
    print(f"Login page status: {response.status_code}")
    
    csrf_token = extract_csrf_token(response.text)
    if not csrf_token:
        print("CSRF token not found in login page")
        return False
    
    # Login as admin user
    login_data = {
        'username': 'e2euser',
        'password': 'password123',
        'csrf_token': csrf_token
    }
    
    response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
    print(f"Login response status: {response.status_code}")
    
    if response.status_code == 302:
        location = response.headers.get('Location', 'Unknown')
        print(f"Login redirected to: {location}")
        # Follow the redirect with proper URL
        if location.startswith('/'):
            redirect_url = f"{BASE_URL}{location}"
        else:
            redirect_url = location
        final_response = session.get(redirect_url)
        print(f"Final page status: {final_response.status_code}")
        return True
    elif response.status_code == 200:
        # Check if we're still on login page (error) or redirected
        if "Invalid username or password" in response.text:
            print("Login failed - invalid credentials")
            return False
        else:
            print("Login appeared successful (200 status)")
            return True
    else:
        print(f"Unexpected login response status: {response.status_code}")
        return False

def test_admin_dashboard():
    """Test admin dashboard access"""
    print("\nTesting admin dashboard...")
    
    response = session.get(f"{BASE_URL}/admin/dashboard")
    print(f"Admin dashboard status: {response.status_code}")
    
    if response.status_code == 200:
        print("[OK] Admin dashboard accessible")
        return True
    else:
        print("[FAIL] Admin dashboard not accessible")
        return False

def test_admin_users():
    """Test admin user management"""
    print("\nTesting admin user management...")
    
    response = session.get(f"{BASE_URL}/admin/users")
    print(f"Admin users page status: {response.status_code}")
    
    if response.status_code == 200:
        print("[OK] Admin users page accessible")
        return True
    else:
        print("[FAIL] Admin users page not accessible")
        return False

def test_admin_ollama_settings():
    """Test admin Ollama settings"""
    print("\nTesting admin Ollama settings...")
    
    response = session.get(f"{BASE_URL}/admin/settings/ollama")
    print(f"Ollama settings page status: {response.status_code}")
    
    if response.status_code == 200:
        print("[OK] Ollama settings page accessible")
        return True
    else:
        print("[FAIL] Ollama settings page not accessible")
        return False

def test_admin_logs():
    """Test admin system logs"""
    print("\nTesting admin system logs...")
    
    response = session.get(f"{BASE_URL}/admin/logs")
    print(f"System logs page status: {response.status_code}")
    
    if response.status_code == 200:
        print("[OK] System logs page accessible")
        return True
    else:
        print("[FAIL] System logs page not accessible")
        return False

def test_admin_api():
    """Test admin API endpoints"""
    print("\nTesting admin API endpoints...")
    
    # Test Ollama connection API
    api_data = {
        'ollama_url': 'http://74.76.44.128:11434'
    }
    
    response = session.post(f"{BASE_URL}/admin/api/test-ollama", 
                           json=api_data,
                           headers={'Content-Type': 'application/json'})
    print(f"Ollama test API status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Ollama connection test result: {result}")
        return True
    else:
        print("[FAIL] Ollama test API not working")
        return False

def extract_csrf_token(html):
    """Extract CSRF token from HTML"""
    import re
    # Try both id and name attributes
    match = re.search(r'id="csrf_token"[^>]*value="([^"]+)"', html)
    if match:
        return match.group(1)
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    if match:
        return match.group(1)
    return None

def test_unauthorized_access():
    """Test that admin areas require authentication"""
    print("\nTesting unauthorized access protection...")
    
    # Create new session without login
    test_session = requests.Session()
    
    admin_urls = [
        "/admin/dashboard",
        "/admin/users", 
        "/admin/settings/ollama",
        "/admin/logs",
        "/admin/maintenance"
    ]
    
    for url in admin_urls:
        response = test_session.get(f"{BASE_URL}{url}", allow_redirects=False)
        if response.status_code == 302:  # Should redirect to login
            location = response.headers.get('Location', '')
            if 'auth/login' in location:
                print(f"[OK] {url} properly protected (redirects to login)")
            else:
                print(f"[WARN] {url} redirects but not to login: {location}")
        else:
            print(f"[FAIL] {url} not properly protected (status: {response.status_code})")

def main():
    print("Starting admin functionality manual tests...")
    print("=" * 50)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(3)
    
    # Test unauthorized access first
    test_unauthorized_access()
    
    # Test admin login
    if not test_admin_login():
        print("Login failed, skipping other tests")
        return
    
    # Test admin functionality
    results = []
    results.append(test_admin_dashboard())
    results.append(test_admin_users())
    results.append(test_admin_ollama_settings())
    results.append(test_admin_logs())
    results.append(test_admin_api())
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("SUCCESS: All admin functionality tests passed!")
    else:
        print("FAILURE: Some tests failed")

if __name__ == "__main__":
    main()