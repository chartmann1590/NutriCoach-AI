import 'package:flutter/material.dart';
import '../models/notification.dart' as app_notification;
import '../services/api_service.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({Key? key}) : super(key: key);

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<app_notification.Notification> _notifications = [];
  bool _isLoading = true;
  bool _hasError = false;
  String _errorMessage = '';
  int _unreadCount = 0;
  bool _showUnreadOnly = false;
  final ScrollController _scrollController = ScrollController();
  bool _hasMore = true;
  bool _isLoadingMore = false;

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    // Add a small delay to ensure the screen is properly initialized
    WidgetsBinding.instance?.addPostFrameCallback((_) {
      _loadNotifications(refresh: true);
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels ==
            _scrollController.position.maxScrollExtent &&
        _hasMore &&
        !_isLoadingMore) {
      _loadMoreNotifications();
    }
  }

  Future<void> _loadNotifications({bool refresh = false}) async {
    if (!refresh && _isLoading) return;

    print('NotificationsScreen: _loadNotifications called, refresh=$refresh, showUnreadOnly=$_showUnreadOnly');

    setState(() {
      if (refresh) {
        _notifications.clear();
        _hasMore = true;
      }
      _isLoading = refresh || _notifications.isEmpty;
      _hasError = false;
    });

    try {
      print('NotificationsScreen: About to call ApiService.getNotifications');
      final response = await ApiService.getNotifications(
        limit: 20,
        offset: refresh ? 0 : _notifications.length,
        unreadOnly: _showUnreadOnly,
      );
      print('NotificationsScreen: Got response, success=${response.success}');

      if (response.success) {
        setState(() {
          if (refresh) {
            _notifications = response.notifications;
          } else {
            _notifications.addAll(response.notifications);
          }
          _unreadCount = response.unreadCount;
          _hasMore = response.hasMore;
          _isLoading = false;
          _hasError = false;
        });
      } else {
        setState(() {
          _hasError = true;
          _errorMessage = response.message ?? 'Failed to load notifications';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _hasError = true;
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadMoreNotifications() async {
    if (_isLoadingMore || !_hasMore) return;

    setState(() {
      _isLoadingMore = true;
    });

    try {
      final response = await ApiService.getNotifications(
        limit: 20,
        offset: _notifications.length,
        unreadOnly: _showUnreadOnly,
      );

      if (response.success) {
        setState(() {
          _notifications.addAll(response.notifications);
          _hasMore = response.hasMore;
          _isLoadingMore = false;
        });
      } else {
        setState(() {
          _isLoadingMore = false;
        });
        _showSnackBar(response.message ?? 'Failed to load more notifications');
      }
    } catch (e) {
      setState(() {
        _isLoadingMore = false;
      });
      _showSnackBar(e.toString());
    }
  }

  Future<void> _markAsRead(app_notification.Notification notification) async {
    if (notification.isRead) return;

    try {
      final success = await ApiService.markNotificationRead(notification.id);
      if (success) {
        setState(() {
          final index = _notifications.indexWhere((n) => n.id == notification.id);
          if (index >= 0) {
            _notifications[index] = app_notification.Notification(
              id: notification.id,
              title: notification.title,
              message: notification.message,
              type: notification.type,
              category: notification.category,
              priority: notification.priority,
              isRead: true,
              createdAt: notification.createdAt,
              readAt: DateTime.now(),
            );
          }
          _unreadCount = (_unreadCount > 0) ? _unreadCount - 1 : 0;
        });
      }
    } catch (e) {
      _showSnackBar('Failed to mark notification as read');
    }
  }

  Future<void> _markAllAsRead() async {
    if (_unreadCount == 0) return;

    try {
      final success = await ApiService.markAllNotificationsRead();
      if (success) {
        setState(() {
          _notifications = _notifications.map((notification) =>
              app_notification.Notification(
                id: notification.id,
                title: notification.title,
                message: notification.message,
                type: notification.type,
                category: notification.category,
                priority: notification.priority,
                isRead: true,
                createdAt: notification.createdAt,
                readAt: DateTime.now(),
              )
          ).toList();
          _unreadCount = 0;
        });
        _showSnackBar('All notifications marked as read');
      }
    } catch (e) {
      _showSnackBar('Failed to mark all notifications as read');
    }
  }

  Future<void> _deleteNotification(app_notification.Notification notification) async {
    try {
      final success = await ApiService.deleteNotification(notification.id);
      if (success) {
        setState(() {
          _notifications.removeWhere((n) => n.id == notification.id);
          if (!notification.isRead) {
            _unreadCount = (_unreadCount > 0) ? _unreadCount - 1 : 0;
          }
        });
        _showSnackBar('Notification deleted');
      }
    } catch (e) {
      _showSnackBar('Failed to delete notification');
    }
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Color _getPriorityColor(String priority) {
    switch (priority) {
      case 'urgent':
        return Colors.red;
      case 'high':
        return Colors.orange;
      case 'normal':
      default:
        return Colors.blue;
    }
  }

  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'meal_reminder':
        return Icons.restaurant;
      case 'goal_achieved':
        return Icons.emoji_events;
      case 'weigh_in_reminder':
        return Icons.monitor_weight;
      case 'admin_message':
        return Icons.admin_panel_settings;
      case 'system':
        return Icons.settings;
      default:
        return Icons.notifications;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('Notifications'),
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (_unreadCount > 0)
            TextButton(
              onPressed: _markAllAsRead,
              child: const Text(
                'Mark all read',
                style: TextStyle(color: Colors.white),
              ),
            ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'toggle_filter') {
                setState(() {
                  _showUnreadOnly = !_showUnreadOnly;
                });
                _loadNotifications(refresh: true);
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'toggle_filter',
                child: Text(_showUnreadOnly ? 'Show All' : 'Show Unread Only'),
              ),
            ],
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => _loadNotifications(refresh: true),
        child: _buildBody(),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _notifications.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            const Text('Loading notifications...'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => _loadNotifications(refresh: true),
              child: const Text('Retry Loading'),
            ),
          ],
        ),
      );
    }

    if (_hasError && _notifications.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              'Error loading notifications',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w500,
                color: Colors.grey.shade600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _errorMessage,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.grey.shade500,
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => _loadNotifications(refresh: true),
              child: const Text('Try Again'),
            ),
          ],
        ),
      );
    }

    if (_notifications.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              _showUnreadOnly ? Icons.mark_email_read : Icons.notifications_none,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              _showUnreadOnly ? 'No unread notifications' : 'No notifications yet',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w500,
                color: Colors.grey.shade600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _showUnreadOnly
                  ? 'All your notifications have been read'
                  : 'You\'ll receive notifications here when they arrive',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.grey.shade500,
              ),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        if (_unreadCount > 0)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            color: Colors.blue.shade50,
            child: Text(
              '$_unreadCount unread notification${_unreadCount == 1 ? '' : 's'}',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.blue.shade700,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        Expanded(
          child: ListView.separated(
            controller: _scrollController,
            padding: const EdgeInsets.all(16),
            itemCount: _notifications.length + (_isLoadingMore ? 1 : 0),
            separatorBuilder: (context, index) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              if (index >= _notifications.length) {
                return const Center(
                  child: Padding(
                    padding: EdgeInsets.all(16),
                    child: CircularProgressIndicator(),
                  ),
                );
              }

              final notification = _notifications[index];
              return _buildNotificationCard(notification);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildNotificationCard(app_notification.Notification notification) {
    final priorityColor = _getPriorityColor(notification.priority);
    final categoryIcon = _getCategoryIcon(notification.category);

    return Card(
      elevation: notification.isRead ? 2 : 4,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _markAsRead(notification),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            border: notification.isRead 
                ? null 
                : Border.all(color: priorityColor, width: 2),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: priorityColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      categoryIcon,
                      color: priorityColor,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                notification.title,
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: notification.isRead 
                                      ? FontWeight.w500 
                                      : FontWeight.w600,
                                  color: notification.isRead 
                                      ? Colors.grey.shade700 
                                      : Colors.grey.shade900,
                                ),
                              ),
                            ),
                            if (!notification.isRead)
                              Container(
                                width: 8,
                                height: 8,
                                decoration: BoxDecoration(
                                  color: priorityColor,
                                  shape: BoxShape.circle,
                                ),
                              ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          notification.message,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade600,
                            height: 1.3,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color: priorityColor.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                notification.priorityDisplayName,
                                style: TextStyle(
                                  fontSize: 12,
                                  color: priorityColor,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              notification.timeAgoString,
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey.shade500,
                              ),
                            ),
                            const Spacer(),
                            PopupMenuButton<String>(
                              onSelected: (value) {
                                if (value == 'mark_read' && !notification.isRead) {
                                  _markAsRead(notification);
                                } else if (value == 'delete') {
                                  _deleteNotification(notification);
                                }
                              },
                              itemBuilder: (context) => [
                                if (!notification.isRead)
                                  const PopupMenuItem(
                                    value: 'mark_read',
                                    child: Text('Mark as read'),
                                  ),
                                const PopupMenuItem(
                                  value: 'delete',
                                  child: Text('Delete'),
                                ),
                              ],
                              child: Icon(
                                Icons.more_vert,
                                color: Colors.grey.shade400,
                                size: 16,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}