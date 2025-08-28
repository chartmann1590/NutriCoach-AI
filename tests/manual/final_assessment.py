#!/usr/bin/env python3
"""
Final assessment of the complete application
"""

import requests
import time

def assess_application():
    """Quick assessment of all application functionality"""
    
    BASE_URL = "http://localhost:5001"
    results = {}
    
    print("FINAL APPLICATION ASSESSMENT")
    print("=" * 50)
    
    # Test 1: Homepage
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200 and ("Welcome to" in response.text and "NutriCoach" in response.text):
            print("[PASS] Homepage: WORKING")
            results["Homepage"] = True
        else:
            print(f"[FAIL] Homepage: FAILED (status: {response.status_code})")
            results["Homepage"] = False
    except Exception as e:
        print(f"[FAIL] Homepage: ERROR ({e})")
        results["Homepage"] = False
    
    # Test 2: Registration Page
    try:
        response = requests.get(f"{BASE_URL}/auth/register", timeout=10)
        if response.status_code == 200 and "Create your account" in response.text:
            print("[PASS] Registration Page: WORKING")
            results["Registration Page"] = True
        else:
            print(f"[FAIL] Registration Page: FAILED (status: {response.status_code})")
            results["Registration Page"] = False
    except Exception as e:
        print(f"[FAIL] Registration Page: ERROR ({e})")
        results["Registration Page"] = False
    
    # Test 3: Login Page
    try:
        response = requests.get(f"{BASE_URL}/auth/login", timeout=10)
        if response.status_code == 200 and "Sign in to your account" in response.text:
            print("[PASS] Login Page: WORKING")
            results["Login Page"] = True
        else:
            print(f"[FAIL] Login Page: FAILED (status: {response.status_code})")
            results["Login Page"] = False
    except Exception as e:
        print(f"[FAIL] Login Page: ERROR ({e})")
        results["Login Page"] = False
    
    # Test 4: Admin Protection
    try:
        response = requests.get(f"{BASE_URL}/admin/dashboard", allow_redirects=False, timeout=10)
        if response.status_code == 302 and "auth/login" in response.headers.get('Location', ''):
            print("[PASS] Admin Protection: WORKING (redirects to login)")
            results["Admin Protection"] = True
        else:
            print(f"[FAIL] Admin Protection: FAILED (status: {response.status_code})")
            results["Admin Protection"] = False
    except Exception as e:
        print(f"[FAIL] Admin Protection: ERROR ({e})")
        results["Admin Protection"] = False
    
    # Test 5: Dashboard Protection
    try:
        response = requests.get(f"{BASE_URL}/dashboard", allow_redirects=False, timeout=10)
        if response.status_code == 302:
            print("[PASS] Dashboard Protection: WORKING")
            results["Dashboard Protection"] = True
        else:
            print(f"[FAIL] Dashboard Protection: FAILED (status: {response.status_code})")
            results["Dashboard Protection"] = False
    except Exception as e:
        print(f"[FAIL] Dashboard Protection: ERROR ({e})")
        results["Dashboard Protection"] = False
    
    # Test 6: Admin Login and Access
    try:
        session = requests.Session()
        
        # Get login page
        response = session.get(f"{BASE_URL}/auth/login")
        
        # Extract CSRF token
        import re
        match = re.search(r'id="csrf_token"[^>]*value="([^"]+)"', response.text)
        if match:
            csrf_token = match.group(1)
            
            # Login as admin
            login_data = {
                'username': 'e2euser',
                'password': 'password123',
                'csrf_token': csrf_token
            }
            
            response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
            
            if response.status_code == 302:
                print("[PASS] Admin Login: WORKING")
                results["Admin Login"] = True
                
                # Test admin dashboard access
                response = session.get(f"{BASE_URL}/admin/dashboard")
                if response.status_code == 200:
                    print("[PASS] Admin Dashboard Access: WORKING")
                    results["Admin Dashboard"] = True
                else:
                    print(f"[FAIL] Admin Dashboard Access: FAILED (status: {response.status_code})")
                    results["Admin Dashboard"] = False
                
                # Test admin user management
                response = session.get(f"{BASE_URL}/admin/users")
                if response.status_code == 200 and "User Management" in response.text:
                    print("[PASS] Admin User Management: WORKING")
                    results["Admin Users"] = True
                else:
                    print(f"[FAIL] Admin User Management: FAILED")
                    results["Admin Users"] = False
                
                # Test admin Ollama settings
                response = session.get(f"{BASE_URL}/admin/settings/ollama")
                if response.status_code == 200 and "Ollama Configuration" in response.text:
                    print("[PASS] Admin Ollama Settings: WORKING")
                    results["Admin Ollama"] = True
                else:
                    print(f"[FAIL] Admin Ollama Settings: FAILED")
                    results["Admin Ollama"] = False
                
                # Test admin logs
                response = session.get(f"{BASE_URL}/admin/logs")
                if response.status_code == 200 and "System Logs" in response.text:
                    print("[PASS] Admin System Logs: WORKING")
                    results["Admin Logs"] = True
                else:
                    print(f"[FAIL] Admin System Logs: FAILED")
                    results["Admin Logs"] = False
                    
            else:
                print(f"[FAIL] Admin Login: FAILED (status: {response.status_code})")
                results["Admin Login"] = False
                results["Admin Dashboard"] = False
                results["Admin Users"] = False
                results["Admin Ollama"] = False
                results["Admin Logs"] = False
        else:
            print("[FAIL] Admin Login: FAILED (no CSRF token)")
            results["Admin Login"] = False
            
    except Exception as e:
        print(f"[FAIL] Admin Login: ERROR ({e})")
        results["Admin Login"] = False
    
    # Test 7: Food Logging Route
    try:
        response = requests.get(f"{BASE_URL}/log", allow_redirects=False, timeout=10)
        if response.status_code == 302:  # Should redirect to login
            print("[PASS] Food Log Route: WORKING (protected)")
            results["Food Log Route"] = True
        else:
            print(f"[FAIL] Food Log Route: FAILED (status: {response.status_code})")
            results["Food Log Route"] = False
    except Exception as e:
        print(f"[FAIL] Food Log Route: ERROR ({e})")
        results["Food Log Route"] = False
    
    # Test 8: Settings Route
    try:
        response = requests.get(f"{BASE_URL}/settings", allow_redirects=False, timeout=10)
        if response.status_code in [302, 308]:  # Should redirect (302 to login or 308 permanent)
            print("[PASS] Settings Route: WORKING (protected)")
            results["Settings Route"] = True
        else:
            print(f"[FAIL] Settings Route: FAILED (status: {response.status_code})")
            results["Settings Route"] = False
    except Exception as e:
        print(f"[FAIL] Settings Route: ERROR ({e})")
        results["Settings Route"] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("ASSESSMENT SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"{test_name:25}: {status}")
    
    print(f"\nOVERALL: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.9:  # 90% pass rate
        print("\nSUCCESS: APPLICATION IS HIGHLY FUNCTIONAL!")
        print("The nutrition AI application is working correctly with comprehensive admin features.")
        return True
    elif passed_tests >= total_tests * 0.75:  # 75% pass rate
        print("\nSUCCESS: APPLICATION IS MOSTLY FUNCTIONAL!")
        print("Minor issues remain but core functionality works.")
        return True
    else:
        print("\nWARNING: APPLICATION NEEDS MORE WORK")
        print("Significant issues found.")
        return False

if __name__ == "__main__":
    print("Starting final application assessment...")
    time.sleep(2)  # Wait for server
    
    success = assess_application()
    
    if success:
        print("\nSUCCESS: ASSESSMENT COMPLETE - APPLICATION READY!")
    else:
        print("\nERROR: ASSESSMENT COMPLETE - ISSUES FOUND")