#!/usr/bin/env python3
"""
Comprehensive admin functionality test summary
"""

import requests
import time

BASE_URL = "http://127.0.0.1:5001"

def test_admin_functionality():
    """Test all admin functionality comprehensively"""
    print("COMPREHENSIVE ADMIN FUNCTIONALITY TEST")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. Test admin access protection
    print("\n1. TESTING ADMIN ACCESS PROTECTION:")
    admin_urls = [
        "/admin/dashboard",
        "/admin/users", 
        "/admin/settings/ollama",
        "/admin/logs",
        "/admin/maintenance"
    ]
    
    protection_results = []
    for url in admin_urls:
        response = session.get(f"{BASE_URL}{url}", allow_redirects=False)
        if response.status_code == 302 and 'auth/login' in response.headers.get('Location', ''):
            print(f"   [OK] {url} - PROTECTED")
            protection_results.append(True)
        else:
            print(f"   [FAIL] {url} - NOT PROTECTED (status: {response.status_code})")
            protection_results.append(False)
    
    # 2. Test admin login
    print("\n2. TESTING ADMIN LOGIN:")
    
    # Get login page
    response = session.get(f"{BASE_URL}/auth/login")
    if response.status_code == 200:
        print("   [OK] Login page accessible")
        
        # Extract CSRF token
        import re
        match = re.search(r'id="csrf_token"[^>]*value="([^"]+)"', response.text)
        if match:
            csrf_token = match.group(1)
            print("   [OK] CSRF token extracted")
            
            # Login as admin
            login_data = {
                'username': 'e2euser',
                'password': 'password123',
                'csrf_token': csrf_token
            }
            
            response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
            if response.status_code == 302:
                print("   [OK] Admin login successful")
                login_success = True
            else:
                print(f"   [FAIL] Admin login failed (status: {response.status_code})")
                login_success = False
        else:
            print("   [FAIL] CSRF token not found")
            login_success = False
    else:
        print(f"   [FAIL] Login page not accessible (status: {response.status_code})")
        login_success = False
    
    if not login_success:
        print("\nSkipping authenticated tests due to login failure")
        return
    
    # 3. Test admin pages access
    print("\n3. TESTING ADMIN PAGES ACCESS (AFTER LOGIN):")
    
    page_results = []
    
    # Admin dashboard
    response = session.get(f"{BASE_URL}/admin/dashboard")
    if response.status_code == 200:
        print("   [OK] Admin dashboard accessible")
        page_results.append(("dashboard", True))
    else:
        print(f"   [FAIL] Admin dashboard not accessible (status: {response.status_code})")
        page_results.append(("dashboard", False))
    
    # Users management
    response = session.get(f"{BASE_URL}/admin/users")
    if response.status_code == 200:
        print("   [OK] User management accessible")
        page_results.append(("users", True))
    else:
        print(f"   [FAIL] User management not accessible (status: {response.status_code})")
        page_results.append(("users", False))
    
    # Ollama settings
    response = session.get(f"{BASE_URL}/admin/settings/ollama")
    if response.status_code == 200:
        print("   [OK] Ollama settings accessible")
        page_results.append(("ollama", True))
    else:
        print(f"   [FAIL] Ollama settings not accessible (status: {response.status_code})")
        page_results.append(("ollama", False))
    
    # System logs
    response = session.get(f"{BASE_URL}/admin/logs")
    if response.status_code == 200:
        print("   [OK] System logs accessible")
        page_results.append(("logs", True))
    else:
        print(f"   [FAIL] System logs not accessible (status: {response.status_code})")
        page_results.append(("logs", False))
    
    # 4. Test admin API endpoints
    print("\n4. TESTING ADMIN API ENDPOINTS:")
    
    # Test Ollama API
    api_data = {'ollama_url': 'http://74.76.44.128:11434'}
    response = session.post(f"{BASE_URL}/admin/api/test-ollama", 
                           json=api_data,
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        result = response.json()
        print(f"   [OK] Ollama API test successful: {result}")
        api_success = True
    else:
        print(f"   [FAIL] Ollama API test failed (status: {response.status_code})")
        if response.text:
            print(f"      Response: {response.text}")
        api_success = False
    
    # 5. Test main dashboard issue
    print("\n5. TESTING MAIN DASHBOARD:")
    response = session.get(f"{BASE_URL}/dashboard")
    if response.status_code == 200:
        print("   [OK] Main dashboard accessible")
        dashboard_success = True
    else:
        print(f"   [FAIL] Main dashboard not accessible (status: {response.status_code})")
        dashboard_success = False
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Admin Protection: {sum(protection_results)}/{len(protection_results)} working")
    print(f"Admin Login: {'OK' if login_success else 'FAIL'}")
    print(f"Admin Pages: {sum(1 for _, success in page_results if success)}/{len(page_results)} working")
    print(f"Admin API: {'OK' if api_success else 'FAIL'}")
    print(f"Main Dashboard: {'OK' if dashboard_success else 'FAIL'}")
    
    total_tests = len(protection_results) + 1 + len(page_results) + 1 + 1
    passed_tests = sum(protection_results) + (1 if login_success else 0) + sum(1 for _, success in page_results if success) + (1 if api_success else 0) + (1 if dashboard_success else 0)
    
    print(f"\nOVERALL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests >= total_tests - 2:  # Allow 2 failures
        print("SUCCESS: ADMIN SYSTEM IS MOSTLY FUNCTIONAL!")
    else:
        print("WARNING: ADMIN SYSTEM NEEDS MORE WORK")

if __name__ == "__main__":
    print("Waiting for server to be ready...")
    time.sleep(2)
    test_admin_functionality()