import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../widgets/dashboard_content.dart';
import 'coach_screen.dart';
import 'server_setup_screen.dart';
import 'food_search_screen.dart';

class MainNavigation extends StatefulWidget {
  const MainNavigation({Key? key}) : super(key: key);

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;
  final GlobalKey<CoachScreenState> _coachKey = GlobalKey<CoachScreenState>();
  
  final List<String> _titles = [
    'Dashboard',
    'AI Coach',
  ];

  void _showQuickActions() {
    _coachKey.currentState?.showQuickActions();
  }

  void _clearChatHistory() {
    _coachKey.currentState?.clearHistory();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: Text(_titles[_currentIndex]),
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (_currentIndex == 1) // AI Coach actions
            IconButton(
              icon: const Icon(Icons.lightbulb),
              onPressed: _showQuickActions,
              tooltip: 'Quick Actions',
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
              if (_currentIndex == 1) // AI Coach specific menu item
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
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.smart_toy),
            label: 'AI Coach',
          ),
        ],
      ),
    );
  }
}