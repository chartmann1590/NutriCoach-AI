import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/food_log.dart';
import '../models/food_item.dart';

class ApiService {
  static String? _baseUrl;
  static String? _sessionCookie;

  static String? get baseUrl => _baseUrl;
  static bool get isConfigured => _baseUrl != null;
  static bool get isAuthenticated => _sessionCookie != null;

  static void configure(String baseUrl) {
    _baseUrl = baseUrl.endsWith('/') ? baseUrl.substring(0, baseUrl.length - 1) : baseUrl;
  }

  static void setSessionCookie(String cookie) {
    _sessionCookie = cookie;
  }

  static void clearSession() {
    _sessionCookie = null;
  }

  static Map<String, String> get _headers {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    if (_sessionCookie != null) {
      headers['Cookie'] = _sessionCookie!;
    }
    
    return headers;
  }

  // Test server connection
  static Future<bool> testConnection(String url) async {
    try {
      final testUrl = url.endsWith('/') ? url.substring(0, url.length - 1) : url;
      print('Testing connection to: $testUrl/api/health');
      
      final response = await http.get(
        Uri.parse('$testUrl/api/health'),
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'NutriCoach-Mobile/1.0',
        },
      ).timeout(const Duration(seconds: 15));
      
      print('Connection test response: ${response.statusCode}');
      print('Response body: ${response.body}');
      
      return response.statusCode == 200;
    } catch (e) {
      print('Connection test failed with error: $e');
      print('Error type: ${e.runtimeType}');
      return false;
    }
  }

  // Authentication
  static Future<Map<String, dynamic>> login(String username, String password) async {
    if (_baseUrl == null) {
      throw Exception('API not configured. Please set server URL first.');
    }

    try {
      print('Starting login process for user: $username');
      
      // Step 1: GET the login page to obtain CSRF token and any initial cookies
      final getResponse = await http.get(
        Uri.parse('$_baseUrl/auth/login'),
        headers: {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'User-Agent': 'NutriCoach-Mobile/1.0',
        },
      ).timeout(const Duration(seconds: 15));
      
      print('GET login page status: ${getResponse.statusCode}');
      
      // Extract CSRF token from the HTML response
      String? csrfToken;
      final csrfMatch = RegExp(r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"').firstMatch(getResponse.body);
      if (csrfMatch != null) {
        csrfToken = csrfMatch.group(1);
        print('Found CSRF token: ${csrfToken?.substring(0, 10)}...');
      } else {
        print('No CSRF token found in login page');
      }
      
      // Extract any initial cookies from the GET request
      String? initialCookies;
      final setCookieHeader = getResponse.headers['set-cookie'];
      if (setCookieHeader != null) {
        initialCookies = setCookieHeader;
        print('Initial cookies received: ${initialCookies.substring(0, 50)}...');
      }

      // Step 2: POST the login form with CSRF token
      final headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'NutriCoach-Mobile/1.0',
        'Referer': '$_baseUrl/auth/login',
      };
      
      if (initialCookies != null) {
        headers['Cookie'] = initialCookies;
      }

      final postData = <String, String>{
        'username': username,
        'password': password,
      };
      
      if (csrfToken != null) {
        postData['csrf_token'] = csrfToken;
      }

      print('POSTing login form with data keys: ${postData.keys.join(', ')}');

      final postResponse = await http.post(
        Uri.parse('$_baseUrl/auth/login'),
        headers: headers,
        body: postData,
      ).timeout(const Duration(seconds: 15));

      print('POST login status: ${postResponse.statusCode}');
      print('Response headers: ${postResponse.headers}');

      // Step 3: Handle the response
      if (postResponse.statusCode == 302) {
        // Successful login typically returns a redirect (302)
        final location = postResponse.headers['location'];
        print('Login redirect to: $location');
        
        // Extract session cookies from the response
        final loginCookies = postResponse.headers['set-cookie'];
        if (loginCookies != null) {
          _sessionCookie = loginCookies;
          print('Session cookies set: ${loginCookies.substring(0, 50)}...');
          
          // Check if redirect is to dashboard (success) or back to login (failure)
          if (location != null && (location.contains('dashboard') || location.contains('onboarding') || !location.contains('login'))) {
            return {'success': true, 'message': 'Login successful'};
          } else {
            return {'success': false, 'message': 'Login failed: Redirected back to login page'};
          }
        } else {
          return {'success': false, 'message': 'Login failed: No session cookie received'};
        }
      } else if (postResponse.statusCode == 200) {
        // Check if we're still on the login page (indicates failure)
        if (postResponse.body.contains('Sign in to your account') || postResponse.body.contains('Invalid username or password')) {
          return {'success': false, 'message': 'Login failed: Invalid username or password'};
        } else {
          // Might be successful but without redirect
          final loginCookies = postResponse.headers['set-cookie'];
          if (loginCookies != null) {
            _sessionCookie = loginCookies;
            return {'success': true, 'message': 'Login successful'};
          }
        }
      }
      
      return {'success': false, 'message': 'Login failed: Unexpected response (${postResponse.statusCode})'};
      
    } catch (e) {
      print('Login error: $e');
      return {'success': false, 'message': 'Login failed: Network error - $e'};
    }
  }

  static Future<Map<String, dynamic>> register(String username, String password) async {
    if (_baseUrl == null) {
      throw Exception('API not configured. Please set server URL first.');
    }

    try {
      print('Starting registration process for user: $username');
      
      // Step 1: GET the registration page to obtain CSRF token and any initial cookies
      final getResponse = await http.get(
        Uri.parse('$_baseUrl/auth/register'),
        headers: {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'User-Agent': 'NutriCoach-Mobile/1.0',
        },
      ).timeout(const Duration(seconds: 15));
      
      print('GET register page status: ${getResponse.statusCode}');
      
      // Extract CSRF token from the HTML response
      String? csrfToken;
      final csrfMatch = RegExp(r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"').firstMatch(getResponse.body);
      if (csrfMatch != null) {
        csrfToken = csrfMatch.group(1);
        print('Found CSRF token for registration');
      }
      
      // Extract any initial cookies from the GET request
      String? initialCookies;
      final setCookieHeader = getResponse.headers['set-cookie'];
      if (setCookieHeader != null) {
        initialCookies = setCookieHeader;
      }

      // Step 2: POST the registration form with CSRF token
      final headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'NutriCoach-Mobile/1.0',
        'Referer': '$_baseUrl/auth/register',
      };
      
      if (initialCookies != null) {
        headers['Cookie'] = initialCookies;
      }

      final postData = <String, String>{
        'username': username,
        'password': password,
      };
      
      if (csrfToken != null) {
        postData['csrf_token'] = csrfToken;
      }

      final postResponse = await http.post(
        Uri.parse('$_baseUrl/auth/register'),
        headers: headers,
        body: postData,
      ).timeout(const Duration(seconds: 15));

      print('POST register status: ${postResponse.statusCode}');

      // Step 3: Handle the response
      if (postResponse.statusCode == 302) {
        // Successful registration typically returns a redirect (302)
        final location = postResponse.headers['location'];
        print('Registration redirect to: $location');
        
        // Extract session cookies from the response
        final regCookies = postResponse.headers['set-cookie'];
        if (regCookies != null) {
          _sessionCookie = regCookies;
          
          // Check if redirect is to onboarding (success) or back to register (failure)
          if (location != null && (location.contains('onboarding') || location.contains('dashboard') || !location.contains('register'))) {
            return {'success': true, 'message': 'Registration successful'};
          } else {
            return {'success': false, 'message': 'Registration failed: Redirected back to register page'};
          }
        }
      } else if (postResponse.statusCode == 200) {
        // Check if we're still on the register page (indicates failure)
        if (postResponse.body.contains('Username already taken') || postResponse.body.contains('Create Account')) {
          return {'success': false, 'message': 'Registration failed: Username may be taken or invalid data'};
        }
      }
      
      return {'success': false, 'message': 'Registration failed: Unexpected response (${postResponse.statusCode})'};
      
    } catch (e) {
      print('Registration error: $e');
      return {'success': false, 'message': 'Registration failed: Network error - $e'};
    }
  }

  static Future<void> logout() async {
    if (_baseUrl == null) return;

    try {
      await http.get(
        Uri.parse('$_baseUrl/auth/logout'),
        headers: _headers,
      ).timeout(const Duration(seconds: 10));
    } catch (e) {
      print('Logout error: $e');
    } finally {
      clearSession();
    }
  }

  // Dashboard data
  static Future<DashboardData?> getDashboardData() async {
    if (_baseUrl == null || _sessionCookie == null) {
      print('Dashboard: Not authenticated or no base URL');
      return null;
    }

    try {
      print('Dashboard: Requesting data from $_baseUrl/api/analytics/dashboard');
      
      final response = await http.get(
        Uri.parse('$_baseUrl/api/analytics/dashboard'),
        headers: _headers,
      ).timeout(const Duration(seconds: 15));

      print('Dashboard: Response status ${response.statusCode}');
      print('Dashboard: Response body length: ${response.body.length}');
      
      if (response.statusCode == 200) {
        if (response.body.isEmpty) {
          print('Dashboard: Empty response body');
          return null;
        }
        
        try {
          final data = json.decode(response.body);
          print('Dashboard: Parsed data keys: ${data.keys}');
          
          // Log some key data to debug
          if (data['today'] != null) {
            print('Dashboard: Today data keys: ${data['today'].keys}');
          }
          
          return DashboardData.fromJson(data);
        } catch (parseError) {
          print('Dashboard: JSON parse error: $parseError');
          print('Dashboard: Error type: ${parseError.runtimeType}');
          print('Dashboard: Raw response: ${response.body}');
          return null;
        }
      } else if (response.statusCode == 401) {
        clearSession();
        throw Exception('Session expired. Please login again.');
      } else {
        print('Dashboard: API error ${response.statusCode}');
        print('Dashboard: Error response: ${response.body}');
        
        // Try to parse error response
        String errorMessage = 'Dashboard API returned ${response.statusCode}';
        try {
          final errorData = json.decode(response.body);
          if (errorData['error'] != null) {
            errorMessage = errorData['error'];
          }
        } catch (e) {
          // Ignore JSON parse errors for error responses
        }
        
        throw Exception(errorMessage);
      }
    } catch (e) {
      print('Dashboard data error: $e');
      if (e.toString().contains('Session expired')) {
        rethrow;
      }
      return null;
    }
  }

  // Food logs
  static Future<List<FoodLog>> getFoodLogs({String? date, int limit = 50}) async {
    if (_baseUrl == null || _sessionCookie == null) return [];

    try {
      final queryParams = <String, String>{
        'limit': limit.toString(),
      };
      if (date != null) {
        queryParams['date'] = date;
      }

      final uri = Uri.parse('$_baseUrl/api/logs').replace(queryParameters: queryParams);
      final response = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final logs = data['logs'] as List;
        return logs.map((log) => FoodLog.fromJson(log)).toList();
      } else if (response.statusCode == 401) {
        clearSession();
        throw Exception('Session expired. Please login again.');
      } else {
        throw Exception('Failed to load food logs');
      }
    } catch (e) {
      print('Food logs error: $e');
      return [];
    }
  }

  static Future<bool> createFoodLog(Map<String, dynamic> foodData) async {
    if (_baseUrl == null || _sessionCookie == null) return false;

    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/logs'),
        headers: _headers,
        body: json.encode(foodData),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 201) {
        return true;
      } else if (response.statusCode == 401) {
        clearSession();
        throw Exception('Session expired. Please login again.');
      } else {
        print('Failed to create food log: ${response.statusCode} ${response.body}');
        return false;
      }
    } catch (e) {
      print('Create food log error: $e');
      return false;
    }
  }

  static Future<bool> deleteFoodLog(int logId) async {
    if (_baseUrl == null || _sessionCookie == null) return false;

    try {
      final response = await http.delete(
        Uri.parse('$_baseUrl/api/logs/$logId'),
        headers: _headers,
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        return true;
      } else if (response.statusCode == 401) {
        clearSession();
        throw Exception('Session expired. Please login again.');
      } else {
        return false;
      }
    } catch (e) {
      print('Delete food log error: $e');
      return false;
    }
  }

  // Food Search functionality
  static Future<List<FoodSearchResult>> searchFood(String query) async {
    if (_baseUrl == null || _sessionCookie == null) {
      throw Exception('Not authenticated. Please login first.');
    }

    try {
      print('Searching food: $query');

      final response = await http.get(
        Uri.parse('$_baseUrl/api/search_nutrition?q=${Uri.encodeComponent(query)}'),
        headers: _headers,
      ).timeout(const Duration(seconds: 20));

      print('Food search response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final results = data['results'] as List;
        
        print('Found ${results.length} food results');
        
        return results.map((result) => FoodSearchResult.fromJson(result)).toList();
      } else if (response.statusCode == 401) {
        clearSession();
        throw Exception('Session expired. Please login again.');
      } else {
        throw Exception('Food search failed: ${response.statusCode}');
      }
    } catch (e) {
      print('Food search error: $e');
      if (e.toString().contains('Session expired')) {
        rethrow;
      }
      throw Exception('Food search failed: $e');
    }
  }

  static Future<FoodSearchResult?> searchBarcode(String barcode) async {
    if (_baseUrl == null || _sessionCookie == null) {
      throw Exception('Not authenticated. Please login first.');
    }

    try {
      print('Searching barcode: $barcode');

      final response = await http.get(
        Uri.parse('$_baseUrl/api/search_barcode?barcode=${Uri.encodeComponent(barcode)}'),
        headers: _headers,
      ).timeout(const Duration(seconds: 20));

      print('Barcode search response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final result = data['result'];
        
        if (result != null) {
          print('Found barcode result: ${result['name']}');
          return FoodSearchResult.fromJson(result);
        }
        return null;
      } else if (response.statusCode == 404) {
        print('Product not found for barcode: $barcode');
        return null;
      } else if (response.statusCode == 401) {
        clearSession();
        throw Exception('Session expired. Please login again.');
      } else {
        throw Exception('Barcode search failed: ${response.statusCode}');
      }
    } catch (e) {
      print('Barcode search error: $e');
      if (e.toString().contains('Session expired')) {
        rethrow;
      }
      throw Exception('Barcode search failed: $e');
    }
  }
}