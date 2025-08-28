import 'package:flutter/foundation.dart';
import 'api_service.dart';

class AuthService extends ChangeNotifier {
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _errorMessage;
  String? _serverUrl;

  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String? get serverUrl => _serverUrl;
  bool get isServerConfigured => _serverUrl != null && ApiService.isConfigured;

  void setServerUrl(String url) {
    _serverUrl = url;
    ApiService.configure(url);
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
        setServerUrl(url);
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

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final result = await ApiService.login(username, password);
      
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
    } catch (e) {
      print('Logout error: $e');
    } finally {
      _isAuthenticated = false;
      _isLoading = false;
      _errorMessage = null;
      notifyListeners();
    }
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}