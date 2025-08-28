class FoodLog {
  final int id;
  final String foodName;
  final String meal;
  final double grams;
  final double calories;
  final double proteinG;
  final double carbsG;
  final double fatG;
  final double fiberG;
  final double sugarG;
  final double sodiumMg;
  final String source;
  final DateTime loggedAt;

  FoodLog({
    required this.id,
    required this.foodName,
    required this.meal,
    required this.grams,
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.fiberG,
    required this.sugarG,
    required this.sodiumMg,
    required this.source,
    required this.loggedAt,
  });

  factory FoodLog.fromJson(Map<String, dynamic> json) {
    return FoodLog(
      id: json['id'],
      foodName: json['food_name'] ?? '',
      meal: json['meal'] ?? '',
      grams: (json['grams'] ?? 0).toDouble(),
      calories: (json['calories'] ?? 0).toDouble(),
      proteinG: (json['protein_g'] ?? 0).toDouble(),
      carbsG: (json['carbs_g'] ?? 0).toDouble(),
      fatG: (json['fat_g'] ?? 0).toDouble(),
      fiberG: (json['fiber_g'] ?? 0).toDouble(),
      sugarG: (json['sugar_g'] ?? 0).toDouble(),
      sodiumMg: (json['sodium_mg'] ?? 0).toDouble(),
      source: json['source'] ?? 'manual',
      loggedAt: DateTime.parse(json['logged_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'food_name': foodName,
      'meal': meal,
      'grams': grams,
      'calories': calories,
      'protein_g': proteinG,
      'carbs_g': carbsG,
      'fat_g': fatG,
      'fiber_g': fiberG,
      'sugar_g': sugarG,
      'sodium_mg': sodiumMg,
      'source': source,
      'logged_at': loggedAt.toIso8601String(),
    };
  }
}

class DashboardData {
  final TodaySummary today;
  final WeeklySummary weekly;
  final Map<String, dynamic> mealDistribution;
  final Map<String, dynamic> macroDistribution;
  final Streaks streaks;
  final List<dynamic> topFoods;

  DashboardData({
    required this.today,
    required this.weekly,
    required this.mealDistribution,
    required this.macroDistribution,
    required this.streaks,
    required this.topFoods,
  });

  factory DashboardData.fromJson(Map<String, dynamic> json) {
    try {
      return DashboardData(
        today: TodaySummary.fromJson(json['today'] ?? {}),
        weekly: WeeklySummary.fromJson(json['weekly'] ?? {}),
        mealDistribution: _ensureMap(json['meal_distribution']),
        macroDistribution: _ensureMap(json['macro_distribution']),
        streaks: Streaks.fromJson(json['streaks'] ?? {}),
        topFoods: _ensureList(json['top_foods']),
      );
    } catch (e) {
      print('Error parsing DashboardData: $e');
      print('JSON keys: ${json.keys}');
      rethrow;
    }
  }
  
  static Map<String, dynamic> _ensureMap(dynamic value) {
    if (value is Map<String, dynamic>) {
      return value;
    } else if (value is Map) {
      return Map<String, dynamic>.from(value);
    } else {
      return {};
    }
  }
  
  static List<dynamic> _ensureList(dynamic value) {
    if (value is List) {
      return value;
    } else {
      return [];
    }
  }
}

class TodaySummary {
  final Map<String, dynamic> totals;
  final Map<String, dynamic> targets;
  final Map<String, dynamic> remaining;

  TodaySummary({
    required this.totals,
    required this.targets,
    required this.remaining,
  });

  factory TodaySummary.fromJson(Map<String, dynamic> json) {
    return TodaySummary(
      totals: _ensureMapStringDynamic(json['totals']),
      targets: _ensureMapStringDynamic(json['targets']),
      remaining: _ensureMapStringDynamic(json['remaining']),
    );
  }
  
  static Map<String, dynamic> _ensureMapStringDynamic(dynamic value) {
    if (value is Map<String, dynamic>) {
      return value;
    } else if (value is Map) {
      return Map<String, dynamic>.from(value);
    } else {
      return {};
    }
  }
}

class WeeklySummary {
  final int daysLogged;
  final Map<String, dynamic> averages;

  WeeklySummary({
    required this.daysLogged,
    required this.averages,
  });

  factory WeeklySummary.fromJson(Map<String, dynamic> json) {
    return WeeklySummary(
      daysLogged: _ensureInt(json['days_logged']),
      averages: _ensureMapStringDynamic(json['averages']),
    );
  }
  
  static int _ensureInt(dynamic value) {
    if (value is int) return value;
    if (value is num) return value.toInt();
    if (value is String) return int.tryParse(value) ?? 0;
    return 0;
  }
  
  static Map<String, dynamic> _ensureMapStringDynamic(dynamic value) {
    if (value is Map<String, dynamic>) {
      return value;
    } else if (value is Map) {
      return Map<String, dynamic>.from(value);
    } else {
      return {};
    }
  }
}

class Streaks {
  final int currentStreak;
  final int longestStreak;
  final int totalDaysLogged;

  Streaks({
    required this.currentStreak,
    required this.longestStreak,
    required this.totalDaysLogged,
  });

  factory Streaks.fromJson(Map<String, dynamic> json) {
    return Streaks(
      currentStreak: _ensureInt(json['current_streak']),
      longestStreak: _ensureInt(json['longest_streak']),
      totalDaysLogged: _ensureInt(json['total_days_logged']),
    );
  }
  
  static int _ensureInt(dynamic value) {
    if (value is int) return value;
    if (value is num) return value.toInt();
    if (value is String) return int.tryParse(value) ?? 0;
    return 0;
  }
}