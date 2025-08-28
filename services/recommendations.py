from datetime import datetime, timedelta
from sqlalchemy import func
from models import Profile, FoodLog, WeighIn
from extensions import db
from typing import Dict, List, Optional


class RecommendationService:
    
    @staticmethod
    def calculate_daily_targets(user_id: int) -> Dict:
        """Calculate daily calorie and macro targets for a user"""
        profile = Profile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return {
                'calories': 2000,
                'protein_g': 150,
                'carbs_g': 250,
                'fat_g': 67,
                'error': 'Profile not found'
            }
        
        # Calculate BMR using Mifflin-St Jeor equation
        if profile.sex.lower() == 'male':
            bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + 5
        else:
            bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age - 161
        
        # Activity level multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        # Calculate TDEE (Total Daily Energy Expenditure)
        multiplier = activity_multipliers.get(profile.activity_level, 1.375)
        tdee = bmr * multiplier
        
        # Adjust based on goal
        if profile.goal_type == 'lose':
            daily_calories = tdee - 500  # 500 cal deficit for ~1 lb/week loss
        elif profile.goal_type == 'gain':
            daily_calories = tdee + 500  # 500 cal surplus for ~1 lb/week gain
        else:  # maintain
            daily_calories = tdee
        
        # Ensure minimum calories
        daily_calories = max(daily_calories, 1200 if profile.sex.lower() == 'female' else 1500)
        
        # Calculate macros (using common ratios)
        protein_g = profile.weight_kg * 2.2  # 1g per lb body weight
        fat_g = daily_calories * 0.25 / 9  # 25% of calories from fat
        carbs_g = (daily_calories - (protein_g * 4) - (fat_g * 9)) / 4  # Remaining calories from carbs
        
        return {
            'calories': round(daily_calories),
            'protein_g': round(protein_g),
            'carbs_g': round(carbs_g),
            'fat_g': round(fat_g),
            'bmr': round(bmr),
            'tdee': round(tdee)
        }
    
    @staticmethod
    def get_daily_summary(user_id: int, date: datetime = None) -> Dict:
        """Get daily nutrition summary for a user"""
        if date is None:
            date = datetime.utcnow().date()
        
        # Get food logs for the day
        logs = FoodLog.query.filter(
            FoodLog.user_id == user_id,
            func.date(FoodLog.logged_at) == date
        ).all()
        
        # Calculate totals
        totals = {
            'calories': sum(log.calories for log in logs),
            'protein_g': sum(log.protein_g for log in logs),
            'carbs_g': sum(log.carbs_g for log in logs),
            'fat_g': sum(log.fat_g for log in logs),
            'fiber_g': sum(log.fiber_g for log in logs),
            'sugar_g': sum(log.sugar_g for log in logs),
            'sodium_mg': sum(log.sodium_mg for log in logs),
            'meal_breakdown': {}
        }
        
        # Meal breakdown
        for meal in ['breakfast', 'lunch', 'dinner', 'snack']:
            meal_logs = [log for log in logs if log.meal == meal]
            totals['meal_breakdown'][meal] = {
                'calories': sum(log.calories for log in meal_logs),
                'count': len(meal_logs)
            }
        
        # Get targets
        targets = RecommendationService.calculate_daily_targets(user_id)
        
        # Calculate percentages
        if targets['calories'] > 0:
            totals['calories_percent'] = (totals['calories'] / targets['calories']) * 100
            totals['protein_percent'] = (totals['protein_g'] / targets['protein_g']) * 100
            totals['carbs_percent'] = (totals['carbs_g'] / targets['carbs_g']) * 100
            totals['fat_percent'] = (totals['fat_g'] / targets['fat_g']) * 100
        
        return {
            'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
            'totals': totals,
            'targets': targets,
            'remaining': {
                'calories': max(0, targets['calories'] - totals['calories']),
                'protein_g': max(0, targets['protein_g'] - totals['protein_g']),
                'carbs_g': max(0, targets['carbs_g'] - totals['carbs_g']),
                'fat_g': max(0, targets['fat_g'] - totals['fat_g'])
            }
        }
    
    @staticmethod
    def get_weekly_summary(user_id: int, weeks_back: int = 0) -> Dict:
        """Get weekly nutrition summary"""
        # Calculate date range
        today = datetime.utcnow().date()
        start_of_week = today - timedelta(days=today.weekday() + (weeks_back * 7))
        end_of_week = start_of_week + timedelta(days=6)
        
        # Get food logs for the week
        logs = FoodLog.query.filter(
            FoodLog.user_id == user_id,
            func.date(FoodLog.logged_at) >= start_of_week,
            func.date(FoodLog.logged_at) <= end_of_week
        ).all()
        
        # Calculate daily averages
        daily_totals = {}
        for log in logs:
            log_date = log.logged_at.date()
            date_str = log_date.isoformat()  # Convert to string for JSON compatibility
            if date_str not in daily_totals:
                daily_totals[date_str] = {
                    'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fat_g': 0
                }
            
            daily_totals[date_str]['calories'] += log.calories
            daily_totals[date_str]['protein_g'] += log.protein_g
            daily_totals[date_str]['carbs_g'] += log.carbs_g
            daily_totals[date_str]['fat_g'] += log.fat_g
        
        # Calculate averages
        days_with_data = len(daily_totals)
        if days_with_data > 0:
            avg_calories = sum(day['calories'] for day in daily_totals.values()) / days_with_data
            avg_protein = sum(day['protein_g'] for day in daily_totals.values()) / days_with_data
            avg_carbs = sum(day['carbs_g'] for day in daily_totals.values()) / days_with_data
            avg_fat = sum(day['fat_g'] for day in daily_totals.values()) / days_with_data
        else:
            avg_calories = avg_protein = avg_carbs = avg_fat = 0
        
        return {
            'week_start': start_of_week.isoformat() if hasattr(start_of_week, 'isoformat') else str(start_of_week),
            'week_end': end_of_week.isoformat() if hasattr(end_of_week, 'isoformat') else str(end_of_week),
            'days_logged': days_with_data,
            'averages': {
                'calories': round(avg_calories),
                'protein_g': round(avg_protein, 1),
                'carbs_g': round(avg_carbs, 1),
                'fat_g': round(avg_fat, 1)
            },
            'daily_data': daily_totals
        }
    
    @staticmethod
    def get_food_suggestions(user_id: int, meal: str = None, remaining_calories: float = None) -> List[Dict]:
        """Get food suggestions based on user preferences and remaining calories"""
        profile = Profile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return []
        
        # Get user preferences and restrictions
        preferences = profile.get_preferences()
        allergies = profile.get_allergies()
        
        # Common healthy food suggestions organized by meal and dietary preference
        suggestions = {
            'breakfast': {
                'default': [
                    {'name': 'Oatmeal with berries', 'calories': 150, 'protein': 5, 'carbs': 30, 'fat': 3},
                    {'name': 'Greek yogurt with granola', 'calories': 200, 'protein': 15, 'carbs': 25, 'fat': 5},
                    {'name': 'Scrambled eggs with toast', 'calories': 250, 'protein': 15, 'carbs': 20, 'fat': 12},
                    {'name': 'Smoothie bowl', 'calories': 180, 'protein': 8, 'carbs': 35, 'fat': 4}
                ],
                'vegetarian': [
                    {'name': 'Avocado toast', 'calories': 220, 'protein': 6, 'carbs': 25, 'fat': 12},
                    {'name': 'Chia pudding', 'calories': 160, 'protein': 6, 'carbs': 20, 'fat': 8}
                ],
                'vegan': [
                    {'name': 'Overnight oats with almond milk', 'calories': 140, 'protein': 4, 'carbs': 28, 'fat': 4},
                    {'name': 'Smoothie with plant protein', 'calories': 200, 'protein': 12, 'carbs': 30, 'fat': 5}
                ]
            },
            'lunch': {
                'default': [
                    {'name': 'Grilled chicken salad', 'calories': 300, 'protein': 25, 'carbs': 15, 'fat': 15},
                    {'name': 'Turkey sandwich', 'calories': 350, 'protein': 20, 'carbs': 40, 'fat': 12},
                    {'name': 'Quinoa bowl', 'calories': 280, 'protein': 12, 'carbs': 45, 'fat': 8},
                    {'name': 'Soup and salad', 'calories': 250, 'protein': 10, 'carbs': 30, 'fat': 10}
                ],
                'vegetarian': [
                    {'name': 'Caprese salad with mozzarella', 'calories': 280, 'protein': 15, 'carbs': 12, 'fat': 20},
                    {'name': 'Vegetable stir-fry', 'calories': 220, 'protein': 8, 'carbs': 35, 'fat': 8}
                ]
            },
            'dinner': {
                'default': [
                    {'name': 'Baked salmon with vegetables', 'calories': 400, 'protein': 30, 'carbs': 20, 'fat': 22},
                    {'name': 'Lean beef with sweet potato', 'calories': 450, 'protein': 35, 'carbs': 35, 'fat': 18},
                    {'name': 'Chicken stir-fry', 'calories': 350, 'protein': 25, 'carbs': 30, 'fat': 15}
                ],
                'vegetarian': [
                    {'name': 'Lentil curry with rice', 'calories': 320, 'protein': 15, 'carbs': 55, 'fat': 6},
                    {'name': 'Eggplant parmesan', 'calories': 380, 'protein': 18, 'carbs': 25, 'fat': 22}
                ]
            },
            'snack': {
                'default': [
                    {'name': 'Apple with almond butter', 'calories': 150, 'protein': 4, 'carbs': 20, 'fat': 8},
                    {'name': 'Greek yogurt', 'calories': 100, 'protein': 10, 'carbs': 12, 'fat': 0},
                    {'name': 'Mixed nuts', 'calories': 180, 'protein': 6, 'carbs': 6, 'fat': 16},
                    {'name': 'Hummus with carrots', 'calories': 120, 'protein': 4, 'carbs': 15, 'fat': 5}
                ]
            }
        }
        
        # Select appropriate suggestions based on meal and preferences
        meal_suggestions = suggestions.get(meal or 'snack', {})
        
        # Start with default suggestions
        selected_suggestions = meal_suggestions.get('default', [])
        
        # Add preference-specific suggestions
        for pref in preferences:
            if pref in meal_suggestions:
                selected_suggestions.extend(meal_suggestions[pref])
        
        # Filter out allergenic foods (simplified)
        filtered_suggestions = []
        for suggestion in selected_suggestions:
            exclude = False
            name_lower = suggestion['name'].lower()
            
            for allergy in allergies:
                if allergy in name_lower:
                    exclude = True
                    break
            
            if not exclude:
                filtered_suggestions.append(suggestion)
        
        # Filter by remaining calories if provided
        if remaining_calories:
            filtered_suggestions = [
                s for s in filtered_suggestions 
                if s['calories'] <= remaining_calories * 1.2  # Allow 20% overage
            ]
        
        return filtered_suggestions[:5]  # Return top 5 suggestions
    
    @staticmethod
    def get_progress_insights(user_id: int) -> Dict:
        """Get insights about user's progress"""
        # Get recent weigh-ins
        recent_weigh_ins = WeighIn.query.filter_by(user_id=user_id)\
            .order_by(WeighIn.recorded_at.desc())\
            .limit(10).all()
        
        insights = {
            'weight_trend': 'stable',
            'weekly_average_calories': 0,
            'consistency_score': 0,
            'recommendations': []
        }
        
        # Weight trend analysis
        if len(recent_weigh_ins) >= 3:
            weights = [w.weight_kg for w in reversed(recent_weigh_ins)]
            
            # Simple trend analysis
            if weights[-1] < weights[0] - 0.5:
                insights['weight_trend'] = 'decreasing'
            elif weights[-1] > weights[0] + 0.5:
                insights['weight_trend'] = 'increasing'
        
        # Weekly average calories
        weekly_summary = RecommendationService.get_weekly_summary(user_id)
        insights['weekly_average_calories'] = weekly_summary['averages']['calories']
        
        # Consistency score (based on days logged this week)
        insights['consistency_score'] = min(100, (weekly_summary['days_logged'] / 7) * 100)
        
        # Generate recommendations
        if insights['consistency_score'] < 70:
            insights['recommendations'].append("Try to log your meals more consistently to get better insights.")
        
        targets = RecommendationService.calculate_daily_targets(user_id)
        if insights['weekly_average_calories'] < targets['calories'] * 0.8:
            insights['recommendations'].append("You may be eating too few calories. Consider adding healthy snacks.")
        elif insights['weekly_average_calories'] > targets['calories'] * 1.2:
            insights['recommendations'].append("You're exceeding your calorie targets. Try smaller portions or healthier alternatives.")
        
        return insights