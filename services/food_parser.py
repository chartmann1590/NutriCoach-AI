import re
from typing import List, Dict, Optional
from services.nutrition_search import NutritionSearch
from services.vision_classifier import VisionClassifier


class FoodParser:
    def __init__(self):
        self.nutrition_search = NutritionSearch()
        self.vision_classifier = VisionClassifier()
    
    def parse_vision_results(self, vision_items: List[Dict]) -> List[Dict]:
        """Parse vision model results into structured food candidates"""
        candidates = []
        
        for item in vision_items:
            # Extract portion size
            portion_grams = self._parse_portion(item.get('portion', '100g'))
            
            # Search for nutrition data
            nutrition_results = self.nutrition_search.search_food(item['name'])
            
            # Get nutrition estimate
            nutrition = self.nutrition_search.get_nutrition_estimate(item['name'], portion_grams)
            
            candidate = {
                'name': item['name'],
                'portion_grams': portion_grams,
                'confidence': item.get('confidence', 0.7),
                'nutrition': nutrition,
                'search_results': nutrition_results[:3]  # Top 3 search results
            }
            
            candidates.append(candidate)
        
        return candidates
    
    def parse_barcode_to_food(self, barcode: str) -> Optional[Dict]:
        """Parse barcode into food item data"""
        result = self.nutrition_search.search_barcode(barcode)
        
        if result and result.get('nutrition'):
            return {
                'name': result['title'],
                'source': 'barcode',
                'barcode': barcode,
                'nutrition_per_100g': result['nutrition'],
                'image_url': result.get('image_url', ''),
                'url': result.get('url', '')
            }
        
        return None
    
    def parse_text_search(self, query: str) -> List[Dict]:
        """Parse text search into food candidates"""
        results = self.nutrition_search.search_food(query)
        
        candidates = []
        for result in results:
            candidate = {
                'name': result['title'],
                'source': result['source'],
                'snippet': result['snippet'],
                'url': result.get('url', ''),
                'nutrition_per_100g': result.get('nutrition'),
                'image_url': result.get('image_url', '')
            }
            candidates.append(candidate)
        
        return candidates
    
    def estimate_portions_from_description(self, description: str) -> Dict:
        """Estimate portion sizes from text description"""
        # Common portion indicators
        portion_patterns = {
            r'(\d+)\s*cups?': lambda x: float(x) * 240,  # 1 cup ≈ 240ml ≈ 240g for liquids
            r'(\d+)\s*tablespoons?': lambda x: float(x) * 15,
            r'(\d+)\s*teaspoons?': lambda x: float(x) * 5,
            r'(\d+)\s*slices?': lambda x: float(x) * 30,  # Bread slice
            r'(\d+)\s*pieces?': lambda x: float(x) * 50,  # Average piece
            r'(\d+)\s*grams?': lambda x: float(x),
            r'(\d+)\s*g\b': lambda x: float(x),
            r'(\d+)\s*oz': lambda x: float(x) * 28.35,
            r'(\d+)\s*pounds?': lambda x: float(x) * 453.592,
            r'(\d+)\s*lbs?': lambda x: float(x) * 453.592,
            r'small': lambda x: 50,
            r'medium': lambda x: 100,
            r'large': lambda x: 200,
            r'handful': lambda x: 30,
        }
        
        description_lower = description.lower()
        
        for pattern, converter in portion_patterns.items():
            match = re.search(pattern, description_lower)
            if match:
                if match.groups():
                    return {'grams': converter(match.group(1)), 'source': pattern}
                else:
                    return {'grams': converter(None), 'source': pattern}
        
        # Default portion
        return {'grams': 100, 'source': 'default'}
    
    def _parse_portion(self, portion_text: str) -> float:
        """Parse portion text into grams"""
        if not portion_text:
            return 100.0
        
        portion_text = portion_text.lower().strip()
        
        # Extract numbers
        numbers = re.findall(r'\d+\.?\d*', portion_text)
        if not numbers:
            return 100.0
        
        amount = float(numbers[0])
        
        # Convert units to grams
        if 'kg' in portion_text:
            return amount * 1000
        elif 'lb' in portion_text or 'pound' in portion_text:
            return amount * 453.592
        elif 'oz' in portion_text:
            return amount * 28.35
        elif 'cup' in portion_text:
            return amount * 240
        elif 'tbsp' in portion_text or 'tablespoon' in portion_text:
            return amount * 15
        elif 'tsp' in portion_text or 'teaspoon' in portion_text:
            return amount * 5
        elif 'slice' in portion_text:
            return amount * 30
        elif 'piece' in portion_text:
            return amount * 50
        elif 'g' in portion_text or 'gram' in portion_text:
            return amount
        else:
            # Assume grams if no unit specified
            return amount
    
    def merge_nutrition_sources(self, food_name: str, vision_nutrition: Dict = None, 
                              search_nutrition: Dict = None, user_input: Dict = None) -> Dict:
        """Merge nutrition data from multiple sources with priority"""
        
        # Priority order: user_input > search_nutrition > vision_nutrition > defaults
        merged = {
            'calories': 0,
            'protein_g': 0,
            'carbs_g': 0,
            'fat_g': 0,
            'fiber_g': 0,
            'sugar_g': 0,
            'sodium_mg': 0,
            'sources': []
        }
        
        # Apply vision nutrition (lowest priority)
        if vision_nutrition:
            for key in merged:
                if key != 'sources' and key in vision_nutrition:
                    merged[key] = vision_nutrition[key]
            merged['sources'].append('vision')
        
        # Apply search nutrition (medium priority)
        if search_nutrition:
            for key in merged:
                if key != 'sources' and key in search_nutrition and search_nutrition[key] > 0:
                    merged[key] = search_nutrition[key]
            merged['sources'].append('search')
        
        # Apply user input (highest priority)
        if user_input:
            for key in merged:
                if key != 'sources' and key in user_input and user_input[key] is not None:
                    try:
                        merged[key] = float(user_input[key])
                    except (ValueError, TypeError):
                        pass
            merged['sources'].append('user')
        
        return merged
    
    def validate_nutrition_data(self, nutrition: Dict) -> Dict:
        """Validate and sanitize nutrition data"""
        validated = {}
        
        # Define reasonable ranges for nutrition values (per 100g)
        ranges = {
            'calories': (0, 900),
            'protein_g': (0, 100),
            'carbs_g': (0, 100),
            'fat_g': (0, 100),
            'fiber_g': (0, 50),
            'sugar_g': (0, 100),
            'sodium_mg': (0, 10000)
        }
        
        for key, (min_val, max_val) in ranges.items():
            value = nutrition.get(key, 0)
            try:
                value = float(value)
                # Clamp to reasonable range
                value = max(min_val, min(max_val, value))
                validated[key] = round(value, 2)
            except (ValueError, TypeError):
                validated[key] = 0
        
        return validated