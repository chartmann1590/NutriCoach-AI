#!/usr/bin/env python3
"""Test JSON serialization of dashboard data"""

import json
import sys
from app import create_app
from extensions import db
from services.recommendations import RecommendationService
from services.analytics import AnalyticsService

def test_dashboard_json_serialization():
    """Test that dashboard data can be properly serialized to JSON"""
    
    app = create_app('development')
    
    with app.app_context():
        print("Testing JSON serialization of dashboard data...")
        
        try:
            # Mock user_id (use 1 if it exists, or any available user)
            user_id = 1
            
            print(f"1. Testing RecommendationService.get_daily_summary for user {user_id}...")
            today_summary = RecommendationService.get_daily_summary(user_id)
            
            # Test JSON serialization
            try:
                today_json = json.dumps(today_summary)
                print(f"   OK: Today summary JSON serialization: OK ({len(today_json)} chars)")
                print(f"   Keys: {list(today_summary.keys())}")
            except Exception as e:
                print(f"   ERROR: Today summary JSON serialization failed: {e}")
                print(f"   Data: {today_summary}")
                return False
            
            print(f"2. Testing RecommendationService.get_weekly_summary for user {user_id}...")
            weekly_summary = RecommendationService.get_weekly_summary(user_id)
            
            try:
                weekly_json = json.dumps(weekly_summary)
                print(f"   OK: Weekly summary JSON serialization: OK ({len(weekly_json)} chars)")
                print(f"   Keys: {list(weekly_summary.keys())}")
            except Exception as e:
                print(f"   ERROR: Weekly summary JSON serialization failed: {e}")
                print(f"   Data: {weekly_summary}")
                return False
            
            print(f"3. Testing AnalyticsService methods for user {user_id}...")
            
            # Test meal distribution
            try:
                meal_dist = AnalyticsService.get_meal_distribution(user_id, 7)
                meal_json = json.dumps(meal_dist)
                print(f"   OK: Meal distribution JSON serialization: OK")
            except Exception as e:
                print(f"   ERROR: Meal distribution JSON serialization failed: {e}")
                return False
            
            # Test macro distribution
            try:
                macro_dist = AnalyticsService.get_macro_distribution(user_id, 7)
                macro_json = json.dumps(macro_dist)
                print(f"   OK: Macro distribution JSON serialization: OK")
            except Exception as e:
                print(f"   ERROR: Macro distribution JSON serialization failed: {e}")
                return False
            
            # Test streaks
            try:
                streaks = AnalyticsService.get_logging_streaks(user_id)
                streaks_json = json.dumps(streaks)
                print(f"   OK: Streaks JSON serialization: OK")
                print(f"   Streaks data: {streaks}")
            except Exception as e:
                print(f"   ERROR: Streaks JSON serialization failed: {e}")
                return False
            
            # Test top foods
            try:
                top_foods = AnalyticsService.get_top_foods(user_id, 7, 5)
                top_foods_json = json.dumps(top_foods)
                print(f"   OK: Top foods JSON serialization: OK")
            except Exception as e:
                print(f"   ERROR: Top foods JSON serialization failed: {e}")
                return False
            
            # Test complete dashboard structure
            print(f"4. Testing complete dashboard structure...")
            dashboard_data = {
                'today': today_summary,
                'weekly': weekly_summary,
                'meal_distribution': meal_dist,
                'macro_distribution': macro_dist,
                'streaks': streaks,
                'top_foods': top_foods
            }
            
            try:
                complete_json = json.dumps(dashboard_data)
                print(f"   OK: Complete dashboard JSON serialization: OK ({len(complete_json)} chars)")
                print(f"   Dashboard keys: {list(dashboard_data.keys())}")
                
                # Also test that it can be parsed back
                parsed_back = json.loads(complete_json)
                print(f"   OK: JSON round-trip successful")
                
            except Exception as e:
                print(f"   ERROR: Complete dashboard JSON serialization failed: {e}")
                return False
            
            print("\nALL JSON SERIALIZATION TESTS PASSED!")
            return True
            
        except Exception as e:
            print(f"Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_dashboard_json_serialization()
    if success:
        print("\nSUCCESS: Dashboard data is properly JSON serializable!")
    else:
        print("\nERROR: Dashboard data has JSON serialization issues!")
    sys.exit(0 if success else 1)