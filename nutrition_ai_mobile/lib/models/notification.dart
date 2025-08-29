class Notification {
  final int id;
  final String title;
  final String message;
  final String type;
  final String category;
  final String priority;
  final bool isRead;
  final DateTime createdAt;
  final DateTime? readAt;

  Notification({
    required this.id,
    required this.title,
    required this.message,
    required this.type,
    required this.category,
    required this.priority,
    required this.isRead,
    required this.createdAt,
    this.readAt,
  });

  factory Notification.fromJson(Map<String, dynamic> json) {
    return Notification(
      id: json['id'],
      title: json['title'],
      message: json['message'],
      type: json['type'],
      category: json['category'],
      priority: json['priority'],
      isRead: json['is_read'],
      createdAt: DateTime.parse(json['created_at']),
      readAt: json['read_at'] != null ? DateTime.parse(json['read_at']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'message': message,
      'type': type,
      'category': category,
      'priority': priority,
      'is_read': isRead,
      'created_at': createdAt.toIso8601String(),
      'read_at': readAt?.toIso8601String(),
    };
  }

  // Helper methods for UI
  String get priorityDisplayName {
    switch (priority) {
      case 'urgent':
        return 'Urgent';
      case 'high':
        return 'High';
      case 'normal':
      default:
        return 'Normal';
    }
  }

  String get typeDisplayName {
    switch (type) {
      case 'reminder':
        return 'Reminder';
      case 'action':
        return 'Action Required';
      case 'system':
        return 'System';
      case 'achievement':
        return 'Achievement';
      default:
        return 'Notification';
    }
  }

  String get categoryDisplayName {
    switch (category) {
      case 'meal_reminder':
        return 'Meal Reminder';
      case 'goal_achieved':
        return 'Goal Achievement';
      case 'weigh_in_reminder':
        return 'Check-in Reminder';
      case 'admin_message':
        return 'Admin Message';
      case 'system':
        return 'System';
      default:
        return 'General';
    }
  }

  // Time ago display
  String get timeAgoString {
    final now = DateTime.now();
    final difference = now.difference(createdAt);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return '${(difference.inDays / 7).floor()}w ago';
    }
  }
}

class NotificationResponse {
  final bool success;
  final List<Notification> notifications;
  final int totalCount;
  final int unreadCount;
  final bool hasMore;
  final String? message;

  NotificationResponse({
    required this.success,
    required this.notifications,
    required this.totalCount,
    required this.unreadCount,
    required this.hasMore,
    this.message,
  });

  factory NotificationResponse.fromJson(Map<String, dynamic> json) {
    final notificationsJson = json['notifications'] as List<dynamic>? ?? [];
    final notifications = notificationsJson
        .map((n) => Notification.fromJson(n))
        .toList();

    return NotificationResponse(
      success: json['success'] ?? false,
      notifications: notifications,
      totalCount: json['total_count'] ?? 0,
      unreadCount: json['unread_count'] ?? 0,
      hasMore: json['has_more'] ?? false,
      message: json['message'],
    );
  }
}

class NotificationCounts {
  final bool success;
  final int totalCount;
  final int unreadCount;
  final String? message;

  NotificationCounts({
    required this.success,
    required this.totalCount,
    required this.unreadCount,
    this.message,
  });

  factory NotificationCounts.fromJson(Map<String, dynamic> json) {
    return NotificationCounts(
      success: json['success'] ?? false,
      totalCount: json['total_count'] ?? 0,
      unreadCount: json['unread_count'] ?? 0,
      message: json['message'],
    );
  }
}