import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';
import '../models/food_log.dart';
import 'server_setup_screen.dart';
import 'food_search_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  DashboardData? _dashboardData;
  List<FoodLog> _recentLogs = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  double _safeToDouble(dynamic value, [double defaultValue = 0.0]) {
    if (value == null) return defaultValue;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) {
      final parsed = double.tryParse(value);
      return parsed ?? defaultValue;
    }
    return defaultValue;
  }

  Future<void> _loadDashboardData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final dashboardData = await ApiService.getDashboardData();
      final recentLogs = await ApiService.getFoodLogs(limit: 10);
      
      if (mounted) {
        if (dashboardData != null) {
          setState(() {
            _dashboardData = dashboardData;
            _recentLogs = recentLogs;
            _isLoading = false;
          });
        } else {
          setState(() {
            _errorMessage = 'Failed to load dashboard data';
            _isLoading = false;
          });
        }
      }
    } catch (e, stackTrace) {
      if (mounted) {
        print('Dashboard load error: $e');
        print('Stack trace: $stackTrace');
        
        setState(() {
          _errorMessage = 'Failed to load dashboard: ${e.toString()}';
          _isLoading = false;
        });
        
        if (e.toString().contains('Session expired')) {
          _showSessionExpiredDialog();
        }
      }
    }
  }

  void _showSessionExpiredDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Session Expired'),
          content: const Text('Your session has expired. Please log in again.'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _logout();
              },
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _logout() async {
    final authService = Provider.of<AuthService>(context, listen: false);
    await authService.logout();
    
    if (mounted) {
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (context) => const ServerSetupScreen()),
        (route) => false,
      );
    }
  }

  Widget _buildLoadingView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('Loading dashboard...'),
        ],
      ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              'Error loading dashboard',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.red.shade700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _errorMessage ?? 'Unknown error occurred',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.red.shade600,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _loadDashboardData,
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNutritionCard(String title, double current, double target, String unit, Color color) {
    final percentage = target > 0 ? (current / target * 100).clamp(0, 100) : 0.0;
    
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '${current.toStringAsFixed(0)} / ${target.toStringAsFixed(0)} $unit',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: percentage / 100,
              backgroundColor: Colors.grey.shade200,
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
            const SizedBox(height: 4),
            Text(
              '${percentage.toStringAsFixed(0)}%',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentLogItem(FoodLog log) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getMealColor(log.meal),
          child: Icon(
            _getMealIcon(log.meal),
            color: Colors.white,
            size: 20,
          ),
        ),
        title: Text(
          log.foodName,
          style: const TextStyle(fontWeight: FontWeight.w500),
        ),
        subtitle: Text('${log.grams.toStringAsFixed(0)}g • ${log.meal}'),
        trailing: Text(
          '${log.calories.toStringAsFixed(0)} cal',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.blue,
          ),
        ),
      ),
    );
  }

  Color _getMealColor(String meal) {
    switch (meal.toLowerCase()) {
      case 'breakfast':
        return Colors.orange;
      case 'lunch':
        return Colors.green;
      case 'dinner':
        return Colors.purple;
      case 'snack':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  IconData _getMealIcon(String meal) {
    switch (meal.toLowerCase()) {
      case 'breakfast':
        return Icons.wb_sunny;
      case 'lunch':
        return Icons.wb_cloudy;
      case 'dinner':
        return Icons.nights_stay;
      case 'snack':
        return Icons.local_cafe;
      default:
        return Icons.restaurant;
    }
  }

  Widget _buildEmptyDashboard() {
    // Show dashboard with default/empty values
    final emptyTotals = <String, dynamic>{
      'calories': 0,
      'protein_g': 0,
      'carbs_g': 0,
      'fat_g': 0,
    };
    final defaultTargets = <String, dynamic>{
      'calories': 2000,
      'protein_g': 150,
      'carbs_g': 250,
      'fat_g': 67,
    };
    
    return RefreshIndicator(
      onRefresh: _loadDashboardData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome Card
            Card(
              elevation: 6,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  gradient: LinearGradient(
                    colors: [Colors.blue.shade600, Colors.blue.shade400],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Welcome to NutriCoach!',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Start logging food to see your nutrition data',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 20),
            
            // Today's Nutrition (with default targets)
            const Text(
              'Today\'s Nutrition Goals',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            
            GridView.count(
              crossAxisCount: 2,
              crossAxisSpacing: 8,
              mainAxisSpacing: 8,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildNutritionCard(
                  'Calories',
                  _safeToDouble(emptyTotals['calories']),
                  _safeToDouble(defaultTargets['calories']),
                  'cal',
                  Colors.blue,
                ),
                _buildNutritionCard(
                  'Protein',
                  _safeToDouble(emptyTotals['protein_g']),
                  _safeToDouble(defaultTargets['protein_g']),
                  'g',
                  Colors.red,
                ),
                _buildNutritionCard(
                  'Carbs',
                  _safeToDouble(emptyTotals['carbs_g']),
                  _safeToDouble(defaultTargets['carbs_g']),
                  'g',
                  Colors.orange,
                ),
                _buildNutritionCard(
                  'Fat',
                  _safeToDouble(emptyTotals['fat_g']),
                  _safeToDouble(defaultTargets['fat_g']),
                  'g',
                  Colors.purple,
                ),
              ],
            ),
            
            const SizedBox(height: 24),
            
            // No food logs message
            const Text(
              'Recent Food Logs',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Icon(
                      Icons.restaurant_menu,
                      size: 48,
                      color: Colors.grey.shade400,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'No food logs yet',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey.shade600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Start logging your meals to track your nutrition',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade500,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboardContent() {
    if (_dashboardData == null) {
      // Show default dashboard with empty data
      return _buildEmptyDashboard();
    }

    final today = _dashboardData!.today;
    final totals = today.totals;
    final targets = today.targets;
    
    return RefreshIndicator(
      onRefresh: _loadDashboardData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome Card
            Card(
              elevation: 6,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  gradient: LinearGradient(
                    colors: [Colors.blue.shade600, Colors.blue.shade400],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Welcome to NutriCoach!',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Track your nutrition goals and stay healthy',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 20),
            
            // Today's Nutrition
            const Text(
              'Today\'s Nutrition',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            
            GridView.count(
              crossAxisCount: 2,
              crossAxisSpacing: 8,
              mainAxisSpacing: 8,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildNutritionCard(
                  'Calories',
                  _safeToDouble(totals['calories']),
                  _safeToDouble(targets['calories'], 2000),
                  'cal',
                  Colors.blue,
                ),
                _buildNutritionCard(
                  'Protein',
                  _safeToDouble(totals['protein_g']),
                  _safeToDouble(targets['protein_g'], 150),
                  'g',
                  Colors.red,
                ),
                _buildNutritionCard(
                  'Carbs',
                  _safeToDouble(totals['carbs_g']),
                  _safeToDouble(targets['carbs_g'], 250),
                  'g',
                  Colors.orange,
                ),
                _buildNutritionCard(
                  'Fat',
                  _safeToDouble(totals['fat_g']),
                  _safeToDouble(targets['fat_g'], 67),
                  'g',
                  Colors.purple,
                ),
              ],
            ),
            
            const SizedBox(height: 24),
            
            // Recent Food Logs
            const Text(
              'Recent Food Logs',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            
            if (_recentLogs.isEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      Icon(
                        Icons.restaurant_menu,
                        size: 48,
                        color: Colors.grey.shade400,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'No food logs yet',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey.shade600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Start logging your meals to track your nutrition',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade500,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              )
            else
              Column(
                children: _recentLogs.take(5).map((log) => _buildRecentLogItem(log)).toList(),
              ),
              
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('Dashboard'),
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'logout') {
                _logout();
              } else if (value == 'refresh') {
                _loadDashboardData();
              }
            },
            itemBuilder: (BuildContext context) {
              return [
                PopupMenuItem<String>(
                  value: 'refresh',
                  child: Row(
                    children: const [
                      Icon(Icons.refresh),
                      SizedBox(width: 8),
                      Text('Refresh'),
                    ],
                  ),
                ),
                PopupMenuItem<String>(
                  value: 'logout',
                  child: Row(
                    children: const [
                      Icon(Icons.logout),
                      SizedBox(width: 8),
                      Text('Logout'),
                    ],
                  ),
                ),
              ];
            },
          ),
        ],
      ),
      body: _isLoading
          ? _buildLoadingView()
          : Column(
              children: [
                // Show error banner if there's an error but still show dashboard
                if (_errorMessage != null)
                  Container(
                    width: double.infinity,
                    color: Colors.orange.shade100,
                    padding: const EdgeInsets.all(8),
                    child: Row(
                      children: [
                        Icon(Icons.warning_amber, color: Colors.orange.shade800, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Unable to sync with server. Showing offline data.',
                            style: TextStyle(
                              color: Colors.orange.shade800,
                              fontSize: 12,
                            ),
                          ),
                        ),
                        TextButton(
                          onPressed: _loadDashboardData,
                          child: Text(
                            'Retry',
                            style: TextStyle(
                              color: Colors.orange.shade800,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                // Always show dashboard content (with fallback if no data)
                Expanded(child: _buildDashboardContent()),
              ],
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => const FoodSearchScreen(),
            ),
          );
        },
        backgroundColor: Colors.green.shade600,
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text('Log Food', style: TextStyle(color: Colors.white)),
      ),
    );
  }
}