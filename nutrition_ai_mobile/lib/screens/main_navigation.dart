import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';
import '../widgets/dashboard_content.dart';
import 'coach_screen.dart';
import 'server_setup_screen.dart';
import 'food_search_screen.dart';
import 'notifications_screen.dart';
import '../models/notification.dart' as app_notification;

class MainNavigation extends StatefulWidget {
  const MainNavigation({Key? key}) : super(key: key);

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;
  final GlobalKey<CoachScreenState> _coachKey = GlobalKey<CoachScreenState>();
  int _unreadNotificationCount = 0;
  
  final List<String> _titles = [
    'Dashboard',
    'Notifications',
    'AI Coach',
  ];

  void _showQuickActions() {
    _coachKey.currentState?.showQuickActions();
  }

  void _clearChatHistory() {
    _coachKey.currentState?.clearHistory();
  }

  @override
  void initState() {
    super.initState();
    _loadNotificationCounts();
  }

  Future<void> _loadNotificationCounts() async {
    try {
      final counts = await ApiService.getNotificationCounts();
      if (counts.success && mounted) {
        setState(() {
          _unreadNotificationCount = counts.unreadCount;
        });
      }
    } catch (e) {
      // Silently handle errors - notification counts are not critical
      print('Failed to load notification counts: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    print('MainNavigation: Building with currentIndex: $_currentIndex, unreadCount: $_unreadNotificationCount');
    return Scaffold(
      backgroundColor: Colors.red.shade100, // TEMP: Make background red to verify MainNavigation is loading
      appBar: AppBar(
        title: Text('MAIN NAVIGATION - ${_titles[_currentIndex]}'), // TEMP: Clear title to verify
        backgroundColor: Colors.green.shade600, // TEMP: Make app bar green
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (_currentIndex == 2) // AI Coach actions
            IconButton(
              icon: const Icon(Icons.lightbulb),
              onPressed: _showQuickActions,
              tooltip: 'Quick Actions',
            ),
          if (_currentIndex == 1) // Notifications screen actions
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _loadNotificationCounts,
              tooltip: 'Refresh',
            ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'logout') {
                Provider.of<AuthService>(context, listen: false).logout();
              } else if (value == 'server_setup') {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const ServerSetupScreen(),
                  ),
                );
              } else if (value == 'clear_history') {
                _clearChatHistory();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'server_setup',
                child: Text('Server Settings'),
              ),
              if (_currentIndex == 2) // AI Coach specific menu item
                const PopupMenuItem(
                  value: 'clear_history',
                  child: Text('Clear Chat History'),
                ),
              const PopupMenuItem(
                value: 'logout',
                child: Text('Logout'),
              ),
            ],
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: [
          const DashboardContent(),
          const NotificationsScreen(),
          CoachScreen(key: _coachKey),
        ],
      ),
      floatingActionButton: _currentIndex == 0 ? FloatingActionButton.extended(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => const FoodSearchScreen(),
            ),
          );
        },
        icon: const Icon(Icons.add),
        label: const Text('Log Food'),
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
      ) : null,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Colors.blue.shade600,
        unselectedItemColor: Colors.grey.shade600,
        backgroundColor: Colors.white,
        elevation: 8,
        items: [
          const BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: _unreadNotificationCount > 0
                ? Stack(
                    children: [
                      const Icon(Icons.notifications),
                      Positioned(
                        right: 0,
                        top: 0,
                        child: Container(
                          padding: const EdgeInsets.all(2),
                          decoration: BoxDecoration(
                            color: Colors.red,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          constraints: const BoxConstraints(
                            minWidth: 12,
                            minHeight: 12,
                          ),
                          child: Text(
                            '$_unreadNotificationCount',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 8,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      ),
                    ],
                  )
                : const Icon(Icons.notifications),
            label: 'Notifications',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.smart_toy),
            label: 'AI Coach',
          ),
        ],
      ),
    );
  }
}