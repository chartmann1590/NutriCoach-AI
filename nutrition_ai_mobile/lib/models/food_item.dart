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