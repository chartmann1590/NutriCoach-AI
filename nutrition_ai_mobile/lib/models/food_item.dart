class FoodSearchResult {
  final String id;
  final String name;
  final String? brand;
  final double calories;
  final double proteinG;
  final double carbsG;
  final double fatG;
  final double fiberG;
  final double sugarG;
  final double sodiumMg;
  final String source;
  final String? imageUrl;
  final double? portionGrams;

  FoodSearchResult({
    required this.id,
    required this.name,
    this.brand,
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.fiberG,
    required this.sugarG,
    required this.sodiumMg,
    required this.source,
    this.imageUrl,
    this.portionGrams,
  });

  factory FoodSearchResult.fromJson(Map<String, dynamic> json) {
    // Handle Flask API response format
    final nutrition = json['nutrition'] as Map<String, dynamic>?;
    
    // Extract name and brand from title
    final title = json['title'] ?? json['name'] ?? '';
    String name = title;
    String? brand;
    
    // Try to extract brand from snippet or parse from title
    if (json['snippet'] != null && json['snippet'].toString().startsWith('Brand: ')) {
      brand = json['snippet'].toString().replaceFirst('Brand: ', '').trim();
      if (brand.isEmpty) brand = null;
    }
    
    return FoodSearchResult(
      id: json['barcode']?.toString() ?? json['id']?.toString() ?? '',
      name: name,
      brand: brand,
      calories: nutrition != null ? _parseDouble(nutrition['calories_per_100g']) : 0.0,
      proteinG: nutrition != null ? _parseDouble(nutrition['protein_per_100g']) : 0.0,
      carbsG: nutrition != null ? _parseDouble(nutrition['carbs_per_100g']) : 0.0,
      fatG: nutrition != null ? _parseDouble(nutrition['fat_per_100g']) : 0.0,
      fiberG: nutrition != null ? _parseDouble(nutrition['fiber_per_100g']) : 0.0,
      sugarG: nutrition != null ? _parseDouble(nutrition['sugar_per_100g']) : 0.0,
      sodiumMg: nutrition != null ? _parseDouble(nutrition['sodium_per_100g']) * 1000 : 0.0, // Convert g to mg
      source: json['source'] ?? 'unknown',
      imageUrl: json['image_url'],
      portionGrams: json['portion_grams'] != null ? _parseDouble(json['portion_grams']) : null,
    );
  }

  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) {
      return double.tryParse(value) ?? 0.0;
    }
    return 0.0;
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'brand': brand,
      'calories': calories,
      'protein_g': proteinG,
      'carbs_g': carbsG,
      'fat_g': fatG,
      'fiber_g': fiberG,
      'sugar_g': sugarG,
      'sodium_mg': sodiumMg,
      'source': source,
      'image_url': imageUrl,
      'portion_grams': portionGrams,
    };
  }

  // Helper method to create a FoodLogEntry for logging
  Map<String, dynamic> toLogEntry({
    required String meal,
    required double grams,
  }) {
    // Scale nutrition values based on grams (values are per 100g)
    final scaleFactor = grams / 100.0;
    
    return {
      'custom_name': name,
      'meal': meal,
      'grams': grams,
      'calories': calories * scaleFactor,
      'protein_g': proteinG * scaleFactor,
      'carbs_g': carbsG * scaleFactor,
      'fat_g': fatG * scaleFactor,
      'fiber_g': fiberG * scaleFactor,
      'sugar_g': sugarG * scaleFactor,
      'sodium_mg': sodiumMg * scaleFactor,
      'source': source,
    };
  }
}

class PhotoFoodCandidate {
  final String name;
  final double portionGrams;
  final double confidence;
  final NutritionInfo? nutrition;
  final List<FoodSearchResult>? searchResults;

  PhotoFoodCandidate({
    required this.name,
    required this.portionGrams,
    required this.confidence,
    this.nutrition,
    this.searchResults,
  });

  factory PhotoFoodCandidate.fromJson(Map<String, dynamic> json) {
    return PhotoFoodCandidate(
      name: json['name'] ?? '',
      portionGrams: _parseDouble(json['portion_grams'] ?? json['portion']),
      confidence: _parseDouble(json['confidence']),
      nutrition: json['nutrition'] != null 
          ? NutritionInfo.fromJson(json['nutrition']) 
          : null,
      searchResults: json['search_results'] != null
          ? (json['search_results'] as List)
              .map((item) => FoodSearchResult.fromJson(item))
              .toList()
          : null,
    );
  }

  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) {
      return double.tryParse(value) ?? 0.0;
    }
    return 0.0;
  }
}

class NutritionInfo {
  final double calories;
  final double proteinG;
  final double carbsG;
  final double fatG;
  final double fiberG;
  final double sugarG;
  final double sodiumMg;
  final String? source;

  NutritionInfo({
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.fiberG,
    required this.sugarG,
    required this.sodiumMg,
    this.source,
  });

  factory NutritionInfo.fromJson(Map<String, dynamic> json) {
    return NutritionInfo(
      calories: _parseDouble(json['calories']),
      proteinG: _parseDouble(json['protein_g']),
      carbsG: _parseDouble(json['carbs_g']),
      fatG: _parseDouble(json['fat_g']),
      fiberG: _parseDouble(json['fiber_g']),
      sugarG: _parseDouble(json['sugar_g']),
      sodiumMg: _parseDouble(json['sodium_mg']),
      source: json['source'],
    );
  }

  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) {
      return double.tryParse(value) ?? 0.0;
    }
    return 0.0;
  }
}

class PhotoAnalysisResult {
  final List<PhotoFoodCandidate> candidates;
  final String? error;
  final String? warning;
  final String? analysisSource;

  PhotoAnalysisResult({
    required this.candidates,
    this.error,
    this.warning,
    this.analysisSource,
  });

  factory PhotoAnalysisResult.fromJson(Map<String, dynamic> json) {
    return PhotoAnalysisResult(
      candidates: json['candidates'] != null
          ? (json['candidates'] as List)
              .map((item) => PhotoFoodCandidate.fromJson(item))
              .toList()
          : [],
      error: json['error'],
      warning: json['warning'],
      analysisSource: json['analysis_source'],
    );
  }
}