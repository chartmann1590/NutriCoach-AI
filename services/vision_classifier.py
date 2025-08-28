from PIL import Image
import json
import random
from typing import List, Dict, Optional
from flask import current_app


class VisionClassifier:
    """Fallback vision classifier using mock classification when PyTorch is not available"""
    
    def __init__(self):
        self.food_classes = self._load_food_classes()
        self.initialized = True
    
    def _load_food_classes(self) -> List[str]:
        """Load Food-101 class labels"""
        # Food-101 class names (simplified selection)
        classes = [
            'apple_pie', 'baby_back_ribs', 'baklava', 'beef_carpaccio', 'beef_tartare',
            'beet_salad', 'beignets', 'bibimbap', 'bread_pudding', 'breakfast_burrito',
            'bruschetta', 'caesar_salad', 'cannoli', 'caprese_salad', 'carrot_cake',
            'ceviche', 'cheese_plate', 'cheesecake', 'chicken_curry', 'chicken_quesadilla',
            'chicken_wings', 'chocolate_cake', 'chocolate_mousse', 'churros', 'clam_chowder',
            'club_sandwich', 'crab_cakes', 'creme_brulee', 'croque_madame', 'cup_cakes',
            'deviled_eggs', 'donuts', 'dumplings', 'edamame', 'eggs_benedict',
            'escargots', 'falafel', 'filet_mignon', 'fish_and_chips', 'foie_gras',
            'french_fries', 'french_onion_soup', 'french_toast', 'fried_calamari', 'fried_rice',
            'frozen_yogurt', 'garlic_bread', 'gnocchi', 'greek_salad', 'grilled_cheese_sandwich',
            'grilled_salmon', 'guacamole', 'gyoza', 'hamburger', 'hot_and_sour_soup',
            'hot_dog', 'huevos_rancheros', 'hummus', 'ice_cream', 'lasagna',
            'lobster_bisque', 'lobster_roll_sandwich', 'macaroni_and_cheese', 'macarons', 'miso_soup',
            'mussels', 'nachos', 'omelette', 'onion_rings', 'oysters',
            'pad_thai', 'paella', 'pancakes', 'panna_cotta', 'peking_duck',
            'pho', 'pizza', 'pork_chop', 'poutine', 'prime_rib',
            'pulled_pork_sandwich', 'ramen', 'ravioli', 'red_velvet_cake', 'risotto',
            'samosa', 'sashimi', 'scallops', 'seaweed_salad', 'shrimp_and_grits',
            'spaghetti_bolognese', 'spaghetti_carbonara', 'spring_rolls', 'steak', 'strawberry_shortcake',
            'sushi', 'tacos', 'takoyaki', 'tiramisu', 'tuna_tartare', 'waffles'
        ]
        return classes
    
    def _initialize_model(self) -> bool:
        """Initialize the vision model - simplified mock version"""
        self.initialized = True
        return True
    
    def classify_image(self, image_path: str) -> List[Dict]:
        """Classify food items in an image using mock classification"""
        try:
            # Load image to validate it exists and is valid
            image = Image.open(image_path).convert('RGB')
            
            # Return mock classification results for testing
            return self._mock_classification()
            
        except Exception as e:
            current_app.logger.error(f"Error in image classification: {e}")
            return self._mock_classification()
    
    def _map_imagenet_to_food(self, imagenet_idx: int) -> Optional[str]:
        """Map ImageNet class index to food item (simplified mapping)"""
        # This is a very simplified mapping - in practice you'd want a proper food classifier
        food_mappings = {
            # Common food-related ImageNet classes
            950: 'lemon',
            951: 'orange',
            952: 'banana',
            953: 'apple',
            954: 'strawberry',
            924: 'pizza',
            925: 'hamburger',
            926: 'hot_dog',
            927: 'ice_cream',
            928: 'bagel',
            929: 'pretzel',
            930: 'sandwich',
            # Add more mappings as needed
        }
        
        # If we have a direct mapping, use it
        if imagenet_idx in food_mappings:
            return food_mappings[imagenet_idx]
        
        # Otherwise, use a random food from our list for demonstration
        import random
        if imagenet_idx < len(self.food_classes):
            # Clean up the food name
            food_name = self.food_classes[imagenet_idx % len(self.food_classes)]
            return food_name.replace('_', ' ').title()
        
        return None
    
    def _estimate_portion_from_image(self) -> str:
        """Estimate portion size from image (placeholder implementation)"""
        # For testing, return a random portion size
        portions = ['50g', '100g', '150g', '200g', '1 cup', '1 slice', '1 piece']
        return random.choice(portions)
    
    def _mock_classification(self) -> List[Dict]:
        """Return mock classification results when the real classifier fails"""
        if current_app:
            current_app.logger.info("Using mock classification results")
        
        # Return some common food items with varied confidence
        mock_results = [
            {'name': 'Grilled Chicken', 'portion': self._estimate_portion_from_image(), 'confidence': 0.75},
            {'name': 'Mixed Vegetables', 'portion': self._estimate_portion_from_image(), 'confidence': 0.65},
            {'name': 'Rice', 'portion': self._estimate_portion_from_image(), 'confidence': 0.60}
        ]
        
        return mock_results
    
    def is_available(self) -> bool:
        """Check if the vision classifier is available"""
        return self.initialized