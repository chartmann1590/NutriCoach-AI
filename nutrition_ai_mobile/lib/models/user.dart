class User {
  final int id;
  final String username;
  final bool isAdmin;
  final bool isActive;
  final DateTime createdAt;
  final DateTime? lastLogin;
  final Profile? profile;

  User({
    required this.id,
    required this.username,
    required this.isAdmin,
    required this.isActive,
    required this.createdAt,
    this.lastLogin,
    this.profile,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      isAdmin: json['is_admin'] ?? false,
      isActive: json['is_active'] ?? true,
      createdAt: DateTime.parse(json['created_at']),
      lastLogin: json['last_login'] != null 
          ? DateTime.parse(json['last_login']) 
          : null,
      profile: json['profile'] != null 
          ? Profile.fromJson(json['profile'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'is_admin': isAdmin,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
      'last_login': lastLogin?.toIso8601String(),
      'profile': profile?.toJson(),
    };
  }
}

class Profile {
  final int id;
  final int userId;
  final String name;
  final int age;
  final String sex;
  final double heightCm;
  final double weightKg;
  final String activityLevel;
  final String goalType;
  final double? targetWeightKg;
  final int? timeframeWeeks;
  final List<String> preferences;
  final List<String> allergies;
  final List<String> conditions;

  Profile({
    required this.id,
    required this.userId,
    required this.name,
    required this.age,
    required this.sex,
    required this.heightCm,
    required this.weightKg,
    required this.activityLevel,
    required this.goalType,
    this.targetWeightKg,
    this.timeframeWeeks,
    this.preferences = const [],
    this.allergies = const [],
    this.conditions = const [],
  });

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: json['id'],
      userId: json['user_id'],
      name: json['name'],
      age: json['age'],
      sex: json['sex'],
      heightCm: json['height_cm'].toDouble(),
      weightKg: json['weight_kg'].toDouble(),
      activityLevel: json['activity_level'],
      goalType: json['goal_type'],
      targetWeightKg: json['target_weight_kg']?.toDouble(),
      timeframeWeeks: json['timeframe_weeks'],
      preferences: json['preferences'] != null 
          ? List<String>.from(json['preferences'])
          : [],
      allergies: json['allergies'] != null 
          ? List<String>.from(json['allergies'])
          : [],
      conditions: json['conditions'] != null 
          ? List<String>.from(json['conditions'])
          : [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'name': name,
      'age': age,
      'sex': sex,
      'height_cm': heightCm,
      'weight_kg': weightKg,
      'activity_level': activityLevel,
      'goal_type': goalType,
      'target_weight_kg': targetWeightKg,
      'timeframe_weeks': timeframeWeeks,
      'preferences': preferences,
      'allergies': allergies,
      'conditions': conditions,
    };
  }
}