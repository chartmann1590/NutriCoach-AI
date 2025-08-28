#!/usr/bin/env python3
"""
Database seeding script for NutriCoach
Creates sample data for development and testing.
"""

from app import create_app
from extensions import db
from models import User, Profile, Settings, FoodItem, FoodLog, WeighIn, WaterIntake
from datetime import datetime, timedelta
import random


def create_sample_users():
    """Create sample users with profiles."""
    users_data = [
        {
            'username': 'demo_user',
            'password': 'demo123',
            'profile': {
                'name': 'Demo User',
                'age': 28,
                'sex': 'female',
                'height_cm': 165,
                'weight_kg': 65,
                'activity_level': 'moderate',
                'goal_type': 'lose',
                'target_weight_kg': 60,
                'timeframe_weeks': 16,
                'preferences': ['vegetarian'],
                'allergies': ['nuts'],
                'budget_range': 'medium',
                'cooking_skill': 'intermediate',
                'equipment': ['stove', 'oven', 'microwave', 'blender'],
                'meals_per_day': 3,
                'sleep_schedule': 'flexible'
            }
        },
        {
            'username': 'fitness_enthusiast',
            'password': 'fitness123',
            'profile': {
                'name': 'Alex Fitness',
                'age': 32,
                'sex': 'male',
                'height_cm': 180,
                'weight_kg': 80,
                'activity_level': 'very_active',
                'goal_type': 'gain',
                'target_weight_kg': 85,
                'timeframe_weeks': 20,
                'preferences': ['omnivore'],
                'allergies': [],
                'budget_range': 'high',
                'cooking_skill': 'advanced',
                'equipment': ['stove', 'oven', 'air_fryer', 'blender', 'food_processor'],
                'meals_per_day': 5,
                'sleep_schedule': 'early_bird'
            }
        },
        {
            'username': 'healthy_living',
            'password': 'healthy123',
            'profile': {
                'name': 'Sarah Health',
                'age': 35,
                'sex': 'female',
                'height_cm': 170,
                'weight_kg': 70,
                'activity_level': 'light',
                'goal_type': 'maintain',
                'preferences': ['mediterranean'],
                'allergies': ['dairy'],
                'budget_range': 'medium',
                'cooking_skill': 'beginner',
                'equipment': ['microwave', 'stove'],
                'meals_per_day': 3,
                'sleep_schedule': 'night_owl'
            }
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            print(f"User {user_data['username']} already exists, skipping...")
            continue
        
        # Create user
        user = User(username=user_data['username'])
        user.set_password(user_data['password'])
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create profile
        profile_data = user_data['profile']
        profile = Profile(
            user_id=user.id,
            name=profile_data['name'],
            age=profile_data['age'],
            sex=profile_data['sex'],
            height_cm=profile_data['height_cm'],
            weight_kg=profile_data['weight_kg'],
            activity_level=profile_data['activity_level'],
            goal_type=profile_data['goal_type'],
            target_weight_kg=profile_data.get('target_weight_kg'),
            timeframe_weeks=profile_data.get('timeframe_weeks'),
            budget_range=profile_data['budget_range'],
            cooking_skill=profile_data['cooking_skill'],
            meals_per_day=profile_data['meals_per_day'],
            sleep_schedule=profile_data['sleep_schedule']
        )
        
        # Set JSON fields
        profile.set_preferences(profile_data['preferences'])
        profile.set_allergies(profile_data['allergies'])
        profile.set_conditions([])
        profile.set_equipment(profile_data['equipment'])
        
        db.session.add(profile)
        
        # Create settings
        settings = Settings(
            user_id=user.id,
            ollama_url='http://localhost:11434',
            system_prompt="""You are a supportive nutrition coach. Help users achieve their health goals through evidence-based guidance. 

Guidelines:
- Be encouraging and supportive
- Provide specific, actionable advice
- Reference the user's current nutrition data when relevant
- Suggest foods that fit their preferences and restrictions
- If asked for medical advice, recommend consulting a healthcare professional
- Keep responses concise and practical""",
            safety_mode=True
        )
        db.session.add(settings)
        
        created_users.append(user)
        print(f"Created user: {user_data['username']}")
    
    return created_users


def create_sample_food_items():
    """Create sample food items for the database."""
    food_items = [
        {
            'canonical_name': 'Banana',
            'source': 'openfoodfacts',
            'nutrition': {
                'calories_per_100g': 89,
                'protein_per_100g': 1.1,
                'carbs_per_100g': 23,
                'fat_per_100g': 0.3,
                'fiber_per_100g': 2.6,
                'sugar_per_100g': 12
            }
        },
        {
            'canonical_name': 'Chicken Breast',
            'source': 'openfoodfacts',
            'nutrition': {
                'calories_per_100g': 165,
                'protein_per_100g': 31,
                'carbs_per_100g': 0,
                'fat_per_100g': 3.6,
                'fiber_per_100g': 0,
                'sugar_per_100g': 0
            }
        },
        {
            'canonical_name': 'Brown Rice',
            'source': 'openfoodfacts',
            'nutrition': {
                'calories_per_100g': 111,
                'protein_per_100g': 2.6,
                'carbs_per_100g': 23,
                'fat_per_100g': 0.9,
                'fiber_per_100g': 1.8,
                'sugar_per_100g': 0.4
            }
        },
        {
            'canonical_name': 'Greek Yogurt',
            'source': 'openfoodfacts',
            'nutrition': {
                'calories_per_100g': 59,
                'protein_per_100g': 10,
                'carbs_per_100g': 3.6,
                'fat_per_100g': 0.4,
                'fiber_per_100g': 0,
                'sugar_per_100g': 3.6
            }
        },
        {
            'canonical_name': 'Avocado',
            'source': 'openfoodfacts',
            'nutrition': {
                'calories_per_100g': 160,
                'protein_per_100g': 2,
                'carbs_per_100g': 9,
                'fat_per_100g': 15,
                'fiber_per_100g': 7,
                'sugar_per_100g': 0.7
            }
        }
    ]
    
    for food_data in food_items:
        # Check if food item already exists
        existing_item = FoodItem.query.filter_by(
            canonical_name=food_data['canonical_name']
        ).first()
        
        if existing_item:
            continue
        
        item = FoodItem(
            canonical_name=food_data['canonical_name'],
            source=food_data['source']
        )
        item.set_nutrition(food_data['nutrition'])
        
        db.session.add(item)
        print(f"Created food item: {food_data['canonical_name']}")


def create_sample_food_logs(users):
    """Create sample food logs for users."""
    if not users:
        return
    
    # Sample meals for different times of day
    breakfast_foods = [
        {'name': 'Oatmeal with Berries', 'calories': 150, 'protein': 5, 'carbs': 30, 'fat': 3},
        {'name': 'Greek Yogurt with Granola', 'calories': 200, 'protein': 15, 'carbs': 25, 'fat': 5},
        {'name': 'Scrambled Eggs with Toast', 'calories': 250, 'protein': 15, 'carbs': 20, 'fat': 12},
        {'name': 'Smoothie Bowl', 'calories': 180, 'protein': 8, 'carbs': 35, 'fat': 4}
    ]
    
    lunch_foods = [
        {'name': 'Grilled Chicken Salad', 'calories': 300, 'protein': 25, 'carbs': 15, 'fat': 15},
        {'name': 'Turkey Sandwich', 'calories': 350, 'protein': 20, 'carbs': 40, 'fat': 12},
        {'name': 'Quinoa Bowl', 'calories': 280, 'protein': 12, 'carbs': 45, 'fat': 8},
        {'name': 'Vegetable Stir Fry', 'calories': 220, 'protein': 8, 'carbs': 35, 'fat': 8}
    ]
    
    dinner_foods = [
        {'name': 'Baked Salmon with Vegetables', 'calories': 400, 'protein': 30, 'carbs': 20, 'fat': 22},
        {'name': 'Lean Beef with Sweet Potato', 'calories': 450, 'protein': 35, 'carbs': 35, 'fat': 18},
        {'name': 'Chicken Stir Fry', 'calories': 350, 'protein': 25, 'carbs': 30, 'fat': 15},
        {'name': 'Lentil Curry with Rice', 'calories': 320, 'protein': 15, 'carbs': 55, 'fat': 6}
    ]
    
    snack_foods = [
        {'name': 'Apple with Almond Butter', 'calories': 150, 'protein': 4, 'carbs': 20, 'fat': 8},
        {'name': 'Greek Yogurt', 'calories': 100, 'protein': 10, 'carbs': 12, 'fat': 0},
        {'name': 'Mixed Nuts', 'calories': 180, 'protein': 6, 'carbs': 6, 'fat': 16},
        {'name': 'Hummus with Carrots', 'calories': 120, 'protein': 4, 'carbs': 15, 'fat': 5}
    ]
    
    meal_foods = {
        'breakfast': breakfast_foods,
        'lunch': lunch_foods,
        'dinner': dinner_foods,
        'snack': snack_foods
    }
    
    # Create logs for the past 7 days
    for user in users:
        for days_ago in range(7):
            log_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Create 2-4 meals per day
            num_meals = random.randint(2, 4)
            meals = random.sample(['breakfast', 'lunch', 'dinner', 'snack'], num_meals)
            
            for meal in meals:
                food = random.choice(meal_foods[meal])
                
                # Add some variation to portions
                portion_multiplier = random.uniform(0.8, 1.2)
                
                log = FoodLog(
                    user_id=user.id,
                    custom_name=food['name'],
                    meal=meal,
                    grams=random.randint(80, 200),
                    calories=int(food['calories'] * portion_multiplier),
                    protein_g=food['protein'] * portion_multiplier,
                    carbs_g=food['carbs'] * portion_multiplier,
                    fat_g=food['fat'] * portion_multiplier,
                    fiber_g=random.uniform(1, 5) * portion_multiplier,
                    sugar_g=random.uniform(0, 10) * portion_multiplier,
                    sodium_mg=random.uniform(50, 500) * portion_multiplier,
                    source='manual',
                    logged_at=log_date + timedelta(
                        hours=random.randint(6, 22),
                        minutes=random.randint(0, 59)
                    )
                )
                
                db.session.add(log)
        
        print(f"Created food logs for user: {user.username}")


def create_sample_weigh_ins(users):
    """Create sample weigh-in data."""
    for user in users:
        base_weight = user.profile.weight_kg
        
        # Create weigh-ins for the past 30 days
        for days_ago in range(30):
            if random.random() < 0.3:  # 30% chance of weighing in each day
                log_date = datetime.utcnow() - timedelta(days=days_ago)
                
                # Simulate weight fluctuation
                weight_change = random.uniform(-0.5, 0.5)
                if user.profile.goal_type == 'lose':
                    weight_change -= random.uniform(0, 0.1)  # Slight downward trend
                elif user.profile.goal_type == 'gain':
                    weight_change += random.uniform(0, 0.1)  # Slight upward trend
                
                weight = base_weight + weight_change
                
                weigh_in = WeighIn(
                    user_id=user.id,
                    weight_kg=round(weight, 1),
                    recorded_at=log_date + timedelta(
                        hours=random.randint(6, 10),  # Morning weigh-ins
                        minutes=random.randint(0, 59)
                    )
                )
                
                db.session.add(weigh_in)
        
        print(f"Created weigh-ins for user: {user.username}")


def create_sample_water_intake(users):
    """Create sample water intake data."""
    for user in users:
        # Create water intake for the past 7 days
        for days_ago in range(7):
            log_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # 3-6 water entries per day
            num_entries = random.randint(3, 6)
            
            for i in range(num_entries):
                # Common water amounts
                amounts = [250, 500, 750, 1000]
                amount = random.choice(amounts)
                
                intake = WaterIntake(
                    user_id=user.id,
                    ml=amount,
                    recorded_at=log_date + timedelta(
                        hours=random.randint(6, 22),
                        minutes=random.randint(0, 59)
                    )
                )
                
                db.session.add(intake)
        
        print(f"Created water intake for user: {user.username}")


def main():
    """Main seeding function."""
    app = create_app()
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Create tables if they don't exist
        db.create_all()
        
        # Create sample data
        print("\n1. Creating sample users...")
        users = create_sample_users()
        
        print("\n2. Creating sample food items...")
        create_sample_food_items()
        
        if users:
            print("\n3. Creating sample food logs...")
            create_sample_food_logs(users)
            
            print("\n4. Creating sample weigh-ins...")
            create_sample_weigh_ins(users)
            
            print("\n5. Creating sample water intake...")
            create_sample_water_intake(users)
        
        # Commit all changes
        try:
            db.session.commit()
            print("\n✅ Database seeding completed successfully!")
            
            print("\n📋 Sample user accounts created:")
            for user in users:
                print(f"  - Username: {user.username}, Password: Use the password from the script")
            
            print("\n🚀 You can now log in with any of these accounts to explore the app with sample data.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during seeding: {e}")
            raise


if __name__ == '__main__':
    main()