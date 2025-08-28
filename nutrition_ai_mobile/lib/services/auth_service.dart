import 'package:flutter/foundation.dart';
import 'api_service.dart';
import 'storage_service.dart';

class AuthService extends ChangeNotifier {
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _errorMessage;
  String? _serverUrl;
  bool _isInitialized = false;

  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String? get serverUrl => _serverUrl;
  bool get isServerConfigured => _serverUrl != null && ApiService.isConfigured;
  bool get isInitialized => _isInitialized;

  // Initialize the auth service with stored data
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    _isLoading = true;
    notifyListeners();
    
    try {
      // Load saved server URL
      final savedServerUrl = await StorageService.getServerUrl();
      if (savedServerUrl != null) {
        _serverUrl = savedServerUrl;
        ApiService.configure(savedServerUrl);
      }
      
      // Check for saved session
      final savedCookie = await StorageService.getSessionCookie();
      if (savedCookie != null) {
        ApiService.setSessionCookie(savedCookie);
        _isAuthenticated = true;
      }
      
      _isInitialized = true;
    } catch (e) {
      print('AuthService initialization error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> setServerUrl(String url) async {
    _serverUrl = url;
    ApiService.configure(url);
    await StorageService.saveServerUrl(url);
    notifyListeners();
  }

  Future<bool> testServerConnection(String url) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      print('AuthService: Testing connection to $url');
      final isConnected = await ApiService.testConnection(url);
      
      if (isConnected) {
        await setServerUrl(url);
        _errorMessage = null;
        print('AuthService: Connection successful');
      } else {
        _errorMessage = 'Unable to connect to server. Please check:\n• Server URL is correct\n• Server is running\n• Device can access the server\n• No firewall blocking connection';
        print('AuthService: Connection failed');
      }
      
      return isConnected;
    } catch (e) {
      _errorMessage = 'Connection test failed: $e\n\nTroubleshooting:\n• Check if server is running\n• Verify URL format (http://ip:port)\n• Check network connectivity';
      print('AuthService: Exception during connection test: $e');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> login(String username, String password, {bool rememberMe = false}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final result = await ApiService.login(username, password);
      
      if (result['success']) {
        _isAuthenticated = true;
        _errorMessage = null;
        
        // Save credentials if remember me is checked
        await StorageService.saveCredentials(username, password, rememberMe);
        
        // Save session cookie for auto-login
        if (ApiService.isAuthenticated) {
          // Get the session cookie from ApiService (we'll need to add a getter)
          // For now, we'll save login success state
          await StorageService.saveLastUsername(username);
        }
        
        notifyListeners();
        return true;
      } else {
        _errorMessage = result['message'];
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'Login failed: $e';
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> register(String username, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final result = await ApiService.register(username, password);
      
      if (result['success']) {
        _isAuthenticated = true;
        _errorMessage = null;
        notifyListeners();
        return true;
      } else {
        _errorMessage = result['message'];
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'Registration failed: $e';
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    try {
      await ApiService.logout();
      await StorageService.clearSessionCookie();
    } catch (e) {
      print('Logout error: $e');
    } finally {
      _isAuthenticated = false;
      _isLoading = false;
      _errorMessage = null;
      notifyListeners();
    }
  }

  // Get saved credentials for auto-fill
  Future<Map<String, String?>> getSavedCredentials() async {
    return await StorageService.getCredentials();
  }

  Future<bool> shouldRememberCredentials() async {
    return await StorageService.shouldRememberCredentials();
  }

  Future<String?> getLastUsername() async {
    return await StorageService.getLastUsername();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}