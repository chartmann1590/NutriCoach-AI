import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/food_item.dart';
import 'food_detail_screen.dart';
import 'manual_food_entry_screen.dart';
import 'photo_food_screen.dart';
import '../widgets/expandable_fab.dart';

class FoodSearchScreen extends StatefulWidget {
  const FoodSearchScreen({Key? key}) : super(key: key);

  @override
  _FoodSearchScreenState createState() => _FoodSearchScreenState();
}

class _FoodSearchScreenState extends State<FoodSearchScreen> {
  final _searchController = TextEditingController();
  final _barcodeController = TextEditingController();
  List<FoodSearchResult> _searchResults = [];
  bool _isLoading = false;
  String? _errorMessage;
  bool _showBarcode = false;

  @override
  void dispose() {
    _searchController.dispose();
    _barcodeController.dispose();
    super.dispose();
  }

  Future<void> _searchFood(String query) async {
    if (query.trim().isEmpty) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _searchResults = [];
    });

    try {
      final results = await ApiService.searchFood(query);
      if (mounted) {
        setState(() {
          _searchResults = results;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _searchBarcode(String barcode) async {
    if (barcode.trim().isEmpty) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final result = await ApiService.searchBarcode(barcode);
      if (mounted) {
        if (result != null) {
          // Navigate directly to food detail screen for barcode results
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => FoodDetailScreen(foodItem: result),
            ),
          );
        } else {
          setState(() {
            _errorMessage = 'Product not found for barcode: $barcode';
          });
        }
        setState(() {
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  Widget _buildSearchResult(FoodSearchResult result) {
    // Check if this result has nutrition data
    final hasNutrition = result.calories > 0 || result.proteinG > 0 || result.carbsG > 0 || result.fatG > 0;
    
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: hasNutrition ? Colors.green.shade100 : Colors.orange.shade100,
          child: Icon(
            hasNutrition ? Icons.restaurant : Icons.info_outline,
            color: hasNutrition ? Colors.green.shade600 : Colors.orange.shade600,
            size: 20,
          ),
        ),
        title: Text(
          result.name.isNotEmpty ? result.name : 'Unknown Food',
          style: const TextStyle(fontWeight: FontWeight.w500),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (result.brand != null && result.brand!.isNotEmpty)
              Text(
                'Brand: ${result.brand}',
                style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
              ),
            const SizedBox(height: 2),
            Text(
              hasNutrition 
                ? '${result.calories.toStringAsFixed(0)} cal • ${result.source}'
                : 'No nutrition data • ${result.source}',
              style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
            ),
          ],
        ),
        trailing: hasNutrition 
          ? Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '${result.calories.toStringAsFixed(0)} cal',
                style: TextStyle(
                  color: Colors.blue.shade700,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            )
          : Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey.shade400),
        onTap: hasNutrition 
          ? () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => FoodDetailScreen(foodItem: result),
                ),
              );
            }
          : () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('${result.name} has no nutrition data available'),
                  backgroundColor: Colors.orange,
                  duration: const Duration(seconds: 2),
                ),
              );
            },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('Food Search'),
        backgroundColor: Colors.green.shade600,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(_showBarcode ? Icons.search : Icons.qr_code),
            onPressed: () {
              setState(() {
                _showBarcode = !_showBarcode;
                _errorMessage = null;
                _searchResults = [];
              });
            },
            tooltip: _showBarcode ? 'Text Search' : 'Barcode Search',
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Search Input
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _showBarcode ? 'Barcode Search' : 'Food Search',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _showBarcode ? _barcodeController : _searchController,
                            keyboardType: _showBarcode ? TextInputType.number : TextInputType.text,
                            decoration: InputDecoration(
                              hintText: _showBarcode 
                                  ? 'Enter barcode number...' 
                                  : 'Search for food items...',
                              prefixIcon: Icon(_showBarcode ? Icons.qr_code : Icons.search),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                              filled: true,
                              fillColor: Colors.grey.shade50,
                            ),
                            onSubmitted: (query) {
                              if (_showBarcode) {
                                _searchBarcode(query);
                              } else {
                                _searchFood(query);
                              }
                            },
                          ),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton(
                          onPressed: _isLoading ? null : () {
                            if (_showBarcode) {
                              _searchBarcode(_barcodeController.text);
                            } else {
                              _searchFood(_searchController.text);
                            }
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _showBarcode ? Colors.orange.shade600 : Colors.green.shade600,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          child: _isLoading
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                  ),
                                )
                              : Icon(_showBarcode ? Icons.qr_code_scanner : Icons.search),
                        ),
                      ],
                    ),
                    if (!_showBarcode)
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Text(
                          'Search foods from Open Food Facts and Wikipedia',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade600,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Error Message
            if (_errorMessage != null)
              Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      Icon(Icons.error_outline, color: Colors.red.shade600),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(color: Colors.red.shade700),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            // Loading State
            if (_isLoading)
              Expanded(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: const [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text('Searching foods...'),
                    ],
                  ),
                ),
              ),

            // Search Results
            if (!_isLoading && _searchResults.isNotEmpty)
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${_searchResults.length} results found',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade600,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Expanded(
                      child: ListView.builder(
                        itemCount: _searchResults.length,
                        itemBuilder: (context, index) {
                          return _buildSearchResult(_searchResults[index]);
                        },
                      ),
                    ),
                  ],
                ),
              ),

            // Empty State
            if (!_isLoading && _searchResults.isEmpty && _errorMessage == null)
              Expanded(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        _showBarcode ? Icons.qr_code : Icons.search,
                        size: 64,
                        color: Colors.grey.shade400,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        _showBarcode 
                            ? 'Scan or enter a barcode to find food'
                            : 'Search for foods to log',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey.shade600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _showBarcode
                            ? 'Enter the barcode numbers found on product packaging'
                            : 'Find nutrition information from our food database',
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
          ],
        ),
      ),
      floatingActionButton: ExpandableFab(
        distance: 60,
        children: [
          ActionButton(
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const PhotoFoodScreen(),
                ),
              );
            },
            icon: const Icon(Icons.camera_alt),
            color: Colors.purple.shade600,
            tooltip: 'Photo Analysis',
          ),
          ActionButton(
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const ManualFoodEntryScreen(),
                ),
              );
            },
            icon: const Icon(Icons.edit),
            color: Colors.blue.shade600,
            tooltip: 'Manual Entry',
          ),
        ],
      ),
    );
  }
}

