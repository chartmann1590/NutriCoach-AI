import requests
import json
from typing import Dict, List, Optional
from flask import current_app


class NutritionSearch:
    def __init__(self):
        self.openfoodfacts_url = current_app.config.get('OPENFOODFACTS_API_URL', 'https://world.openfoodfacts.org')
        self.wikipedia_url = current_app.config.get('WIKIPEDIA_API_URL', 'https://en.wikipedia.org')
    
    def search_food(self, query: str) -> List[Dict]:
        """Search for food items across multiple sources"""
        results = []
        
        # Search Open Food Facts
        off_results = self.search_openfoodfacts(query)
        results.extend(off_results)
        
        # Search Wikipedia for general information
        wiki_results = self.search_wikipedia(query)
        results.extend(wiki_results)
        
        return results[:10]  # Limit to top 10 results
    
    def search_openfoodfacts(self, query: str) -> List[Dict]:
        """Search Open Food Facts API"""
        try:
            if current_app.config.get('DISABLE_EXTERNAL_CALLS', False):
                return []
            
            url = f"{self.openfoodfacts_url}/cgi/search.pl"
            params = {
                'search_terms': query,
                'search_simple': 1,
                'action': 'process',
                'json': 1,
                'page_size': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                results = []
                for product in products:
                    result = self._normalize_openfoodfacts_product(product)
                    if result:
                        results.append(result)
                
                return results
            
            return []
        
        except Exception as e:
            current_app.logger.error(f"Error searching Open Food Facts: {e}")
            return []
    
    def search_barcode(self, barcode: str) -> Optional[Dict]:
        """Search for product by barcode"""
        try:
            if current_app.config.get('DISABLE_EXTERNAL_CALLS', False):
                return None
            
            url = f"{self.openfoodfacts_url}/api/v0/product/{barcode}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 1:
                    product = data.get('product', {})
                    return self._normalize_openfoodfacts_product(product)
            
            return None
        
        except Exception as e:
            current_app.logger.error(f"Error searching barcode: {e}")
            return None
    
    def search_wikipedia(self, query: str) -> List[Dict]:
        """Search Wikipedia for food information"""
        try:
            if current_app.config.get('DISABLE_EXTERNAL_CALLS', False):
                return []
            
            # Search for pages
            search_url = f"{self.wikipedia_url}/api/rest_v1/page/summary/{query}"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    'source': 'wikipedia',
                    'title': data.get('title', query),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'snippet': data.get('extract', ''),
                    'nutrition': None  # Wikipedia doesn't provide structured nutrition data
                }
                
                return [result]
            
            return []
        
        except Exception as e:
            current_app.logger.error(f"Error searching Wikipedia: {e}")
            return []
    
    def _normalize_openfoodfacts_product(self, product: Dict) -> Optional[Dict]:
        """Normalize Open Food Facts product data"""
        try:
            # Extract basic information
            name = product.get('product_name', '') or product.get('product_name_en', '')
            brand = product.get('brands', '')
            
            if not name:
                return None
            
            # Extract nutrition data
            nutrients = product.get('nutriments', {})
            nutrition = {
                'calories_per_100g': nutrients.get('energy-kcal_100g', 0),
                'protein_per_100g': nutrients.get('proteins_100g', 0),
                'carbs_per_100g': nutrients.get('carbohydrates_100g', 0),
                'fat_per_100g': nutrients.get('fat_100g', 0),
                'fiber_per_100g': nutrients.get('fiber_100g', 0),
                'sugar_per_100g': nutrients.get('sugars_100g', 0),
                'sodium_per_100g': nutrients.get('sodium_100g', 0),
                'salt_per_100g': nutrients.get('salt_100g', 0)
            }
            
            # Clean up nutrition data
            for key, value in nutrition.items():
                if isinstance(value, str):
                    try:
                        nutrition[key] = float(value)
                    except (ValueError, TypeError):
                        nutrition[key] = 0
                elif value is None:
                    nutrition[key] = 0
            
            return {
                'source': 'openfoodfacts',
                'title': f"{name} {brand}".strip(),
                'url': f"{self.openfoodfacts_url}/product/{product.get('code', '')}",
                'snippet': f"Brand: {brand}" if brand else "",
                'nutrition': nutrition,
                'barcode': product.get('code'),
                'image_url': product.get('image_url', '')
            }
        
        except Exception as e:
            current_app.logger.error(f"Error normalizing product: {e}")
            return None
    
    def get_nutrition_estimate(self, food_name: str, grams: float = 100) -> Dict:
        """Get nutrition estimate for a food item"""
        results = self.search_food(food_name)
        
        # Find the best match with nutrition data
        for result in results:
            if result.get('nutrition') and result['source'] == 'openfoodfacts':
                nutrition = result['nutrition']
                
                # Scale nutrition to the requested grams
                scale_factor = grams / 100
                
                return {
                    'calories': nutrition.get('calories_per_100g', 0) * scale_factor,
                    'protein_g': nutrition.get('protein_per_100g', 0) * scale_factor,
                    'carbs_g': nutrition.get('carbs_per_100g', 0) * scale_factor,
                    'fat_g': nutrition.get('fat_per_100g', 0) * scale_factor,
                    'fiber_g': nutrition.get('fiber_per_100g', 0) * scale_factor,
                    'sugar_g': nutrition.get('sugar_per_100g', 0) * scale_factor,
                    'sodium_mg': nutrition.get('sodium_per_100g', 0) * scale_factor * 1000,  # Convert g to mg
                    'source': result['title']
                }
        
        # Fallback: basic estimates based on food type
        return self._get_basic_estimate(food_name, grams)
    
    def _get_basic_estimate(self, food_name: str, grams: float) -> Dict:
        """Provide basic nutrition estimates for common foods"""
        
        # Simple lookup table for common foods (per 100g)
        basic_foods = {
            'apple': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2},
            'banana': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3},
            'rice': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3},
            'chicken breast': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6},
            'egg': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11},
            'bread': {'calories': 265, 'protein': 9, 'carbs': 49, 'fat': 3.2},
            'milk': {'calories': 42, 'protein': 3.4, 'carbs': 5, 'fat': 1},
        }
        
        # Find the closest match
        food_lower = food_name.lower()
        scale_factor = grams / 100
        
        for key, nutrition in basic_foods.items():
            if key in food_lower:
                return {
                    'calories': nutrition['calories'] * scale_factor,
                    'protein_g': nutrition['protein'] * scale_factor,
                    'carbs_g': nutrition['carbs'] * scale_factor,
                    'fat_g': nutrition['fat'] * scale_factor,
                    'fiber_g': 0,
                    'sugar_g': 0,
                    'sodium_mg': 0,
                    'source': 'Basic estimate'
                }
        
        # Default fallback
        return {
            'calories': 100 * scale_factor,
            'protein_g': 5 * scale_factor,
            'carbs_g': 15 * scale_factor,
            'fat_g': 3 * scale_factor,
            'fiber_g': 0,
            'sugar_g': 0,
            'sodium_mg': 0,
            'source': 'Generic estimate'
        }