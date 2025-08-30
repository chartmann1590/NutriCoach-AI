import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import '../services/api_service.dart';
import '../models/food_item.dart';
import 'food_detail_screen.dart';

class PhotoFoodScreen extends StatefulWidget {
  const PhotoFoodScreen({Key? key}) : super(key: key);

  @override
  _PhotoFoodScreenState createState() => _PhotoFoodScreenState();
}

class _PhotoFoodScreenState extends State<PhotoFoodScreen> {
  final ImagePicker _picker = ImagePicker();
  File? _selectedImage;
  bool _isAnalyzing = false;
  List<PhotoFoodCandidate>? _candidates;
  String? _errorMessage;
  String? _warning;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('Photo Food Log'),
        backgroundColor: Colors.purple.shade600,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Camera Action Cards
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    const Text(
                      'Capture Food Photo',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: _isAnalyzing ? null : () => _takePhoto(ImageSource.camera),
                            icon: const Icon(Icons.camera_alt),
                            label: const Text('Take Photo'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.purple.shade600,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _isAnalyzing ? null : () => _takePhoto(ImageSource.gallery),
                            icon: const Icon(Icons.photo_library),
                            label: const Text('From Gallery'),
                            style: OutlinedButton.styleFrom(
                              backgroundColor: Colors.purple.shade600,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Selected Image Preview
            if (_selectedImage != null)
              Card(
                elevation: 4,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      const Text(
                        'Selected Photo',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.file(
                          _selectedImage!,
                          height: 200,
                          width: double.infinity,
                          fit: BoxFit.cover,
                        ),
                      ),
                      const SizedBox(height: 12),
                      if (!_isAnalyzing && _candidates == null)
                        ElevatedButton.icon(
                          onPressed: _analyzePhoto,
                          icon: const Icon(Icons.analytics),
                          label: const Text('Analyze Food'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green.shade600,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 24),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),

            // Analysis Loading
            if (_isAnalyzing)
              Card(
                elevation: 4,
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    children: const [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text(
                        'Analyzing food photo...',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'This may take a few moments',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

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

            // Warning Message
            if (_warning != null)
              Card(
                color: Colors.orange.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      Icon(Icons.warning_outlined, color: Colors.orange.shade600),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _warning!,
                          style: TextStyle(color: Colors.orange.shade700),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            // Analysis Results
            if (_candidates != null && _candidates!.isNotEmpty)
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${_candidates!.length} food items detected',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey.shade700,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Expanded(
                      child: ListView.builder(
                        itemCount: _candidates!.length,
                        itemBuilder: (context, index) {
                          return _buildCandidateCard(_candidates![index]);
                        },
                      ),
                    ),
                  ],
                ),
              ),

            // Empty State
            if (_selectedImage == null && !_isAnalyzing && _candidates == null)
              Expanded(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.camera_alt,
                        size: 64,
                        color: Colors.grey.shade400,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Take a photo of your food',
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.grey.shade600,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'AI will analyze the photo and identify food items with nutrition information',
                        style: TextStyle(
                          fontSize: 14,
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
    );
  }

  Widget _buildCandidateCard(PhotoFoodCandidate candidate) {
    final confidence = (candidate.confidence * 100).toInt();
    
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.green.shade100,
          child: Icon(
            Icons.restaurant,
            color: Colors.green.shade600,
            size: 20,
          ),
        ),
        title: Text(
          candidate.name,
          style: const TextStyle(fontWeight: FontWeight.w500),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Portion: ${candidate.portionGrams.toInt()}g • Confidence: $confidence%',
              style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
            ),
            if (candidate.nutrition != null)
              Text(
                '${candidate.nutrition!.calories.toStringAsFixed(0)} cal • P: ${candidate.nutrition!.proteinG.toStringAsFixed(0)}g • C: ${candidate.nutrition!.carbsG.toStringAsFixed(0)}g • F: ${candidate.nutrition!.fatG.toStringAsFixed(0)}g',
                style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
              ),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: confidence >= 70 
                ? Colors.green.shade50 
                : confidence >= 50 
                    ? Colors.orange.shade50
                    : Colors.red.shade50,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            '$confidence%',
            style: TextStyle(
              color: confidence >= 70 
                  ? Colors.green.shade700 
                  : confidence >= 50 
                      ? Colors.orange.shade700
                      : Colors.red.shade700,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        onTap: () {
          // Convert to FoodSearchResult for navigation
          final foodItem = FoodSearchResult(
            id: 'photo_${DateTime.now().millisecondsSinceEpoch}',
            name: candidate.name,
            source: 'photo_analysis',
            calories: candidate.nutrition?.calories ?? 0,
            proteinG: candidate.nutrition?.proteinG ?? 0,
            carbsG: candidate.nutrition?.carbsG ?? 0,
            fatG: candidate.nutrition?.fatG ?? 0,
            fiberG: candidate.nutrition?.fiberG ?? 0,
            sugarG: candidate.nutrition?.sugarG ?? 0,
            sodiumMg: candidate.nutrition?.sodiumMg ?? 0,
            portionGrams: candidate.portionGrams,
          );
          
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => FoodDetailScreen(foodItem: foodItem),
            ),
          );
        },
      ),
    );
  }

  Future<void> _takePhoto(ImageSource source) async {
    try {
      // Check and request permissions
      if (source == ImageSource.camera) {
        final permission = await Permission.camera.request();
        if (permission != PermissionStatus.granted) {
          setState(() {
            _errorMessage = 'Camera permission is required to take photos';
          });
          return;
        }
      }

      final XFile? photo = await _picker.pickImage(
        source: source,
        imageQuality: 85,
        maxWidth: 1024,
        maxHeight: 1024,
      );

      if (photo != null) {
        setState(() {
          _selectedImage = File(photo.path);
          _candidates = null;
          _errorMessage = null;
          _warning = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to capture photo: $e';
      });
    }
  }

  Future<void> _analyzePhoto() async {
    if (_selectedImage == null) return;

    setState(() {
      _isAnalyzing = true;
      _errorMessage = null;
      _warning = null;
      _candidates = null;
    });

    try {
      final result = await ApiService.uploadPhotoForAnalysis(_selectedImage!);
      
      if (mounted) {
        setState(() {
          _isAnalyzing = false;
          if (result.candidates.isNotEmpty) {
            _candidates = result.candidates;
            if (result.warning != null) {
              _warning = result.warning;
            }
          } else {
            _errorMessage = result.error ?? 'No food items were detected in the photo';
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isAnalyzing = false;
          _errorMessage = 'Failed to analyze photo: $e';
        });
      }
    }
  }
}