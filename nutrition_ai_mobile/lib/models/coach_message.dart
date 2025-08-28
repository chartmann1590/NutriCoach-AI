class CoachMessage {
  final String role;
  final String content;
  final DateTime timestamp;
  final List<String>? references;

  CoachMessage({
    required this.role,
    required this.content,
    required this.timestamp,
    this.references,
  });

  factory CoachMessage.fromJson(Map<String, dynamic> json) {
    return CoachMessage(
      role: json['role'] ?? 'user',
      content: json['content'] ?? '',
      timestamp: json['created_at'] != null 
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      references: json['refs'] != null 
          ? List<String>.from(json['refs'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'role': role,
      'content': content,
      'created_at': timestamp.toIso8601String(),
      'refs': references,
    };
  }

  bool get isUser => role == 'user';
  bool get isAssistant => role == 'assistant';
  bool get isSystem => role == 'system';
}