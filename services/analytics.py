from datetime import datetime, timedelta
from sqlalchemy import func, and_
from models import FoodLog, WeighIn, WaterIntake, Profile
from extensions import db
from typing import Dict, List, Optional
import json


class AnalyticsService:
    
    @staticmethod
    def get_nutrition_trends(user_id: int, days: int = 30) -> Dict:
        """Get nutrition trends over specified days"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Get daily nutrition totals
        daily_data = db.session.query(
            func.date(FoodLog.logged_at).label('date'),
            func.sum(FoodLog.calories).label('calories'),
            func.sum(FoodLog.protein_g).label('protein'),
            func.sum(FoodLog.carbs_g).label('carbs'),
            func.sum(FoodLog.fat_g).label('fat'),
            func.sum(FoodLog.fiber_g).label('fiber'),
            func.sum(FoodLog.sodium_mg).label('sodium')
        ).filter(
            and_(
                FoodLog.user_id == user_id,
                func.date(FoodLog.logged_at) >= start_date,
                func.date(FoodLog.logged_at) <= end_date
            )
        ).group_by(
            func.date(FoodLog.logged_at)
        ).all()
        
        # Convert to chart-friendly format
        chart_data = {
            'dates': [],
            'calories': [],
            'protein': [],
            'carbs': [],
            'fat': [],
            'fiber': [],
            'sodium': []
        }
        
        # Fill in missing days with zeros
        current_date = start_date
        data_dict = {}
        for row in daily_data:
            date_key = row.date
            if isinstance(date_key, str):
                from datetime import datetime as dt
                date_key = dt.strptime(date_key, '%Y-%m-%d').date()
            data_dict[date_key] = row
        
        while current_date <= end_date:
            chart_data['dates'].append(current_date.isoformat())
            
            if current_date in data_dict:
                row = data_dict[current_date]
                chart_data['calories'].append(float(row.calories or 0))
                chart_data['protein'].append(float(row.protein or 0))
                chart_data['carbs'].append(float(row.carbs or 0))
                chart_data['fat'].append(float(row.fat or 0))
                chart_data['fiber'].append(float(row.fiber or 0))
                chart_data['sodium'].append(float(row.sodium or 0))
            else:
                # No data for this day
                for key in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sodium']:
                    chart_data[key].append(0)
            
            current_date += timedelta(days=1)
        
        return chart_data
    
    @staticmethod
    def get_weight_trends(user_id: int, days: int = 90) -> Dict:
        """Get weight trends over specified days"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        weigh_ins = WeighIn.query.filter(
            and_(
                WeighIn.user_id == user_id,
                func.date(WeighIn.recorded_at) >= start_date,
                func.date(WeighIn.recorded_at) <= end_date
            )
        ).order_by(WeighIn.recorded_at).all()
        
        chart_data = {
            'dates': [],
            'weights': [],
            'trend': []
        }
        
        if weigh_ins:
            for weigh_in in weigh_ins:
                chart_data['dates'].append(weigh_in.recorded_at.date().isoformat())
                chart_data['weights'].append(float(weigh_in.weight_kg))
            
            # Calculate moving average trend
            window_size = min(7, len(chart_data['weights']))
            trend = []
            
            for i in range(len(chart_data['weights'])):
                start_idx = max(0, i - window_size + 1)
                end_idx = i + 1
                avg = sum(chart_data['weights'][start_idx:end_idx]) / (end_idx - start_idx)
                trend.append(round(avg, 1))
            
            chart_data['trend'] = trend
        
        return chart_data
    
    @staticmethod
    def get_meal_distribution(user_id: int, days: int = 30) -> Dict:
        """Get distribution of calories across meals"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        meal_data = db.session.query(
            FoodLog.meal,
            func.sum(FoodLog.calories).label('total_calories'),
            func.count(FoodLog.id).label('count')
        ).filter(
            and_(
                FoodLog.user_id == user_id,
                func.date(FoodLog.logged_at) >= start_date,
                func.date(FoodLog.logged_at) <= end_date
            )
        ).group_by(FoodLog.meal).all()
        
        result = {
            'labels': [],
            'calories': [],
            'counts': []
        }
        
        for row in meal_data:
            result['labels'].append(row.meal.capitalize())
            result['calories'].append(float(row.total_calories))
            result['counts'].append(int(row.count))
        
        return result
    
    @staticmethod
    def get_top_foods(user_id: int, days: int = 30, limit: int = 10) -> List[Dict]:
        """Get most frequently logged foods"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Get foods by frequency and total calories
        top_foods = db.session.query(
            FoodLog.custom_name,
            func.count(FoodLog.id).label('frequency'),
            func.sum(FoodLog.calories).label('total_calories'),
            func.avg(FoodLog.calories).label('avg_calories')
        ).filter(
            and_(
                FoodLog.user_id == user_id,
                func.date(FoodLog.logged_at) >= start_date,
                func.date(FoodLog.logged_at) <= end_date,
                FoodLog.custom_name.isnot(None)
            )
        ).group_by(
            FoodLog.custom_name
        ).order_by(
            func.count(FoodLog.id).desc()
        ).limit(limit).all()
        
        result = []
        for food in top_foods:
            result.append({
                'name': food.custom_name,
                'frequency': int(food.frequency),
                'total_calories': float(food.total_calories),
                'avg_calories': round(float(food.avg_calories), 1)
            })
        
        return result
    
    @staticmethod
    def get_macro_distribution(user_id: int, days: int = 30) -> Dict:
        """Get average macro distribution"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        totals = db.session.query(
            func.sum(FoodLog.protein_g).label('total_protein'),
            func.sum(FoodLog.carbs_g).label('total_carbs'),
            func.sum(FoodLog.fat_g).label('total_fat')
        ).filter(
            and_(
                FoodLog.user_id == user_id,
                func.date(FoodLog.logged_at) >= start_date,
                func.date(FoodLog.logged_at) <= end_date
            )
        ).first()
        
        if not totals or not any([totals.total_protein, totals.total_carbs, totals.total_fat]):
            return {
                'labels': ['Protein', 'Carbs', 'Fat'],
                'values': [0, 0, 0],
                'calories': [0, 0, 0]
            }
        
        # Convert to calories
        protein_cal = float(totals.total_protein or 0) * 4
        carbs_cal = float(totals.total_carbs or 0) * 4
        fat_cal = float(totals.total_fat or 0) * 9
        
        total_cal = protein_cal + carbs_cal + fat_cal
        
        if total_cal == 0:
            return {
                'labels': ['Protein', 'Carbs', 'Fat'],
                'values': [0, 0, 0],
                'calories': [0, 0, 0]
            }
        
        # Calculate percentages
        protein_pct = round((protein_cal / total_cal) * 100, 1)
        carbs_pct = round((carbs_cal / total_cal) * 100, 1)
        fat_pct = round((fat_cal / total_cal) * 100, 1)
        
        return {
            'labels': ['Protein', 'Carbs', 'Fat'],
            'values': [protein_pct, carbs_pct, fat_pct],
            'calories': [round(protein_cal), round(carbs_cal), round(fat_cal)]
        }
    
    @staticmethod
    def get_logging_streaks(user_id: int) -> Dict:
        """Get logging streak information"""
        # Get all distinct logging dates
        logging_dates = db.session.query(
            func.date(FoodLog.logged_at).label('date')
        ).filter(
            FoodLog.user_id == user_id
        ).distinct().order_by(
            func.date(FoodLog.logged_at).desc()
        ).all()
        
        if not logging_dates:
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'total_days_logged': 0
            }
        
        dates = []
        for row in logging_dates:
            date_val = row.date
            if isinstance(date_val, str):
                from datetime import datetime as dt
                date_val = dt.strptime(date_val, '%Y-%m-%d').date()
            dates.append(date_val)
        
        # Calculate current streak
        current_streak = 0
        today = datetime.utcnow().date()
        
        # Check if logged today or yesterday
        if dates and (dates[0] == today or dates[0] == today - timedelta(days=1)):
            current_date = dates[0]
            for date in dates:
                if date == current_date:
                    current_streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
    
        # Calculate longest streak
        longest_streak = 0
        temp_streak = 1
        
        for i in range(1, len(dates)):
            if dates[i-1] - dates[i] == timedelta(days=1):
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
        
        longest_streak = max(longest_streak, temp_streak)
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_days_logged': len(dates)
        }
    
    @staticmethod
    def get_water_intake_trends(user_id: int, days: int = 30) -> Dict:
        """Get water intake trends"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        daily_water = db.session.query(
            func.date(WaterIntake.recorded_at).label('date'),
            func.sum(WaterIntake.ml).label('total_ml')
        ).filter(
            and_(
                WaterIntake.user_id == user_id,
                func.date(WaterIntake.recorded_at) >= start_date,
                func.date(WaterIntake.recorded_at) <= end_date
            )
        ).group_by(
            func.date(WaterIntake.recorded_at)
        ).all()
        
        chart_data = {
            'dates': [],
            'intake_ml': []
        }
        
        # Fill in missing days
        current_date = start_date
        data_dict = {}
        for row in daily_water:
            date_key = row.date
            if isinstance(date_key, str):
                from datetime import datetime as dt
                date_key = dt.strptime(date_key, '%Y-%m-%d').date()
            data_dict[date_key] = row
        
        while current_date <= end_date:
            chart_data['dates'].append(current_date.isoformat())
            
            if current_date in data_dict:
                chart_data['intake_ml'].append(float(data_dict[current_date].total_ml))
            else:
                chart_data['intake_ml'].append(0)
            
            current_date += timedelta(days=1)
        
        return chart_data
    
    @staticmethod
    def export_data(user_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Export user data for CSV download"""
        logs = FoodLog.query.filter(
            and_(
                FoodLog.user_id == user_id,
                FoodLog.logged_at >= start_date,
                FoodLog.logged_at <= end_date
            )
        ).order_by(FoodLog.logged_at).all()
        
        export_data = []
        for log in logs:
            export_data.append({
                'Date': log.logged_at.strftime('%Y-%m-%d'),
                'Time': log.logged_at.strftime('%H:%M'),
                'Meal': log.meal,
                'Food': log.custom_name or (log.food_item.canonical_name if log.food_item else ''),
                'Grams': log.grams,
                'Calories': log.calories,
                'Protein (g)': log.protein_g,
                'Carbs (g)': log.carbs_g,
                'Fat (g)': log.fat_g,
                'Fiber (g)': log.fiber_g,
                'Sugar (g)': log.sugar_g,
                'Sodium (mg)': log.sodium_mg,
                'Source': log.source
            })
        
        return export_data