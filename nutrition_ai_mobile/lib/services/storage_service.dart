import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const String _serverUrlKey = 'server_url';
  static const String _usernameKey = 'username';
  static const String _passwordKey = 'password';
  static const String _rememberCredentialsKey = 'remember_credentials';
  static const String _sessionCookieKey = 'session_cookie';

  static SharedPreferences? _prefs;

  static Future<void> init() async {
    _prefs ??= await SharedPreferences.getInstance();
  }

  // Server URL storage
  static Future<void> saveServerUrl(String url) async {
    await init();
    await _prefs!.setString(_serverUrlKey, url);
  }

  static Future<String?> getServerUrl() async {
    await init();
    return _prefs!.getString(_serverUrlKey);
  }

  // Credentials storage
  static Future<void> saveCredentials(String username, String password, bool remember) async {
    await init();
    if (remember) {
      await _prefs!.setString(_usernameKey, username);
      await _prefs!.setString(_passwordKey, password);
      await _prefs!.setBool(_rememberCredentialsKey, true);
    } else {
      await clearCredentials();
    }
  }

  static Future<Map<String, String?>> getCredentials() async {
    await init();
    final remember = _prefs!.getBool(_rememberCredentialsKey) ?? false;
    if (remember) {
      return {
        'username': _prefs!.getString(_usernameKey),
        'password': _prefs!.getString(_passwordKey),
      };
    }
    return {'username': null, 'password': null};
  }

  static Future<bool> shouldRememberCredentials() async {
    await init();
    return _prefs!.getBool(_rememberCredentialsKey) ?? false;
  }

  static Future<void> clearCredentials() async {
    await init();
    await _prefs!.remove(_usernameKey);
    await _prefs!.remove(_passwordKey);
    await _prefs!.setBool(_rememberCredentialsKey, false);
  }

  // Session storage
  static Future<void> saveSessionCookie(String cookie) async {
    await init();
    await _prefs!.setString(_sessionCookieKey, cookie);
  }

  static Future<String?> getSessionCookie() async {
    await init();
    return _prefs!.getString(_sessionCookieKey);
  }

  static Future<void> clearSessionCookie() async {
    await init();
    await _prefs!.remove(_sessionCookieKey);
  }

  // Clear all data
  static Future<void> clearAll() async {
    await init();
    await _prefs!.clear();
  }

  // Get saved username for display (even if not remembering password)
  static Future<String?> getLastUsername() async {
    await init();
    return _prefs!.getString(_usernameKey);
  }

  // Save just username (for username history)
  static Future<void> saveLastUsername(String username) async {
    await init();
    await _prefs!.setString(_usernameKey, username);
  }
}