import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';
import '../models/food_log.dart';
import '../screens/server_setup_screen.dart';
import '../screens/food_search_screen.dart';

class DashboardContent extends StatefulWidget {
  const DashboardContent({Key? key}) : super(key: key);

  @override
  _DashboardContentState createState() => _DashboardContentState();
}

class _DashboardContentState extends State<DashboardContent> {
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
      print('Loading dashboard data...');
      final data = await ApiService.getDashboardData();
      final logs = await ApiService.getFoodLogs(limit: 10);
      
      if (mounted) {
        setState(() {
          _dashboardData = data;
          _recentLogs = logs;
          _isLoading = false;
        });
      }
    } catch (e) {
      print('Error loading dashboard: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = e.toString();
        });
      }
    }
  }

  Widget _buildEmptyDashboard() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Icon(
                    Icons.cloud_off,
                    size: 48,
                    color: Colors.orange,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Dashboard Offline',
                    style: Theme.of(context).textTheme.headlineSmall,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Unable to load dashboard data. You can still log food manually.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),
          _buildQuickActions(),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Quick Actions',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => const FoodSearchScreen(),
                        ),
                      );
                    },
                    icon: const Icon(Icons.add),
                    label: const Text('Log Food'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue.shade600,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _loadDashboardData,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Refresh'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _loadDashboardData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: _isLoading
            ? const Center(
                child: Padding(
                  padding: EdgeInsets.all(50),
                  child: CircularProgressIndicator(),
                ),
              )
            : _errorMessage != null
                ? _buildErrorState()
                : _dashboardData == null
                    ? _buildEmptyDashboard()
                    : _buildDashboardContent(),
      ),
    );
  }

  Widget _buildErrorState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
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
          const SizedBox(height: 12),
          TextButton(
            onPressed: () {
              setState(() {
                _errorMessage = null;
                _dashboardData = null;
              });
            },
            child: const Text('Use Offline Mode'),
          ),
        ],
      ),
    );
  }

  Widget _buildDashboardContent() {
    if (_dashboardData == null) return _buildEmptyDashboard();

    final today = _dashboardData!.today;
    final totals = today.totals;
    final targets = today.targets;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Today's Progress Card
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Today\'s Progress',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade700,
                  ),
                ),
                const SizedBox(height: 16),
                _buildMacroProgress('Calories', 
                  _safeToDouble(totals['calories']), 
                  _safeToDouble(targets['calories']), 
                  Colors.orange, 
                  'cal'
                ),
                const SizedBox(height: 12),
                _buildMacroProgress('Protein', 
                  _safeToDouble(totals['protein_g']), 
                  _safeToDouble(targets['protein_g']), 
                  Colors.red, 
                  'g'
                ),
                const SizedBox(height: 12),
                _buildMacroProgress('Carbs', 
                  _safeToDouble(totals['carbs_g']), 
                  _safeToDouble(targets['carbs_g']), 
                  Colors.green, 
                  'g'
                ),
                const SizedBox(height: 12),
                _buildMacroProgress('Fat', 
                  _safeToDouble(totals['fat_g']), 
                  _safeToDouble(targets['fat_g']), 
                  Colors.blue, 
                  'g'
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        
        // Recent Food Logs
        if (_recentLogs.isNotEmpty) ...[
          Text(
            'Recent Food Logs',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Card(
            child: ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _recentLogs.length > 5 ? 5 : _recentLogs.length,
              separatorBuilder: (context, index) => const Divider(),
              itemBuilder: (context, index) {
                final log = _recentLogs[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: _getMealColor(log.meal),
                    child: Text(
                      log.meal.substring(0, 1).toUpperCase(),
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ),
                  title: Text(log.foodName),
                  subtitle: Text('${log.calories.toStringAsFixed(0)} cal • ${log.grams.toStringAsFixed(0)}g'),
                  trailing: Text(
                    _formatMealTime(log.meal),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 16),
        ],
        
        // Quick Actions
        _buildQuickActions(),
        const SizedBox(height: 100), // Extra space for FAB
      ],
    );
  }

  Widget _buildMacroProgress(String name, double current, double target, Color color, String unit) {
    double percentage = target > 0 ? (current / target) : 0;
    percentage = percentage.clamp(0.0, 1.0);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              name,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
            Text(
              '${current.toStringAsFixed(target > 100 ? 0 : 1)}/${target.toStringAsFixed(target > 100 ? 0 : 1)} $unit',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: percentage,
          backgroundColor: Colors.grey.shade300,
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      ],
    );
  }

  Color _getMealColor(String meal) {
    switch (meal.toLowerCase()) {
      case 'breakfast':
        return Colors.orange;
      case 'lunch':
        return Colors.green;
      case 'dinner':
        return Colors.blue;
      case 'snack':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  String _formatMealTime(String meal) {
    switch (meal.toLowerCase()) {
      case 'breakfast':
        return 'Morning';
      case 'lunch':
        return 'Afternoon';
      case 'dinner':
        return 'Evening';
      case 'snack':
        return 'Snack';
      default:
        return meal;
    }
  }
}