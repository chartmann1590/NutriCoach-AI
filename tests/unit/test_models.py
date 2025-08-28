import pytest
from datetime import datetime
from models import User, Profile, Settings, FoodLog, FoodItem, CoachMessage, Photo, WeighIn, WaterIntake
from extensions import db


class TestUser:
    
    def test_create_user(self, app):
        """Test user creation."""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('password123')
            
            assert user.username == 'testuser'
            assert user.password_hash is not None
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')

    def test_user_password_hashing(self, app):
        """Test password hashing and verification."""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('password123')
            
            # Password should be hashed
            assert user.password_hash != 'password123'
            
            # Should verify correct password
            assert user.check_password('password123')
            
            # Should reject incorrect password
            assert not user.check_password('wrongpassword')

    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(username='testuser')
            assert repr(user) == '<User testuser>'


class TestProfile:
    
    def test_create_profile(self, app, user):
        """Test profile creation."""
        with app.app_context():
            profile = Profile(
                user_id=user.id,
                name='Test User',
                age=30,
                sex='male',
                height_cm=175,
                weight_kg=75,
                activity_level='moderate',
                goal_type='maintain'
            )
            
            db.session.add(profile)
            db.session.commit()
            
            assert profile.name == 'Test User'
            assert profile.age == 30
            assert profile.user_id == user.id

    def test_profile_json_fields(self, app, user):
        """Test JSON field storage and retrieval."""
        with app.app_context():
            profile = Profile(
                user_id=user.id,
                name='Test User',
                age=30,
                sex='male',
                height_cm=175,
                weight_kg=75,
                activity_level='moderate',
                goal_type='maintain'
            )
            
            # Test preferences
            preferences = ['vegetarian', 'low_sodium']
            profile.set_preferences(preferences)
            assert profile.get_preferences() == preferences
            
            # Test allergies
            allergies = ['nuts', 'dairy']
            profile.set_allergies(allergies)
            assert profile.get_allergies() == allergies
            
            # Test equipment
            equipment = ['stove', 'oven', 'microwave']
            profile.set_equipment(equipment)
            assert profile.get_equipment() == equipment
            
            # Test conditions
            conditions = ['diabetes', 'hypertension']
            profile.set_conditions(conditions)
            assert profile.get_conditions() == conditions


class TestFoodLog:
    
    def test_create_food_log(self, app, user):
        """Test food log creation."""
        with app.app_context():
            log = FoodLog(
                user_id=user.id,
                custom_name='Apple',
                meal='breakfast',
                grams=150,
                calories=80,
                protein_g=0.5,
                carbs_g=20,
                fat_g=0.2,
                source='manual'
            )
            
            db.session.add(log)
            db.session.commit()
            
            assert log.custom_name == 'Apple'
            assert log.meal == 'breakfast'
            assert log.calories == 80
            assert log.user_id == user.id

    def test_food_log_micros_json(self, app, user):
        """Test micronutrients JSON storage."""
        with app.app_context():
            log = FoodLog(
                user_id=user.id,
                custom_name='Apple',
                meal='breakfast',
                grams=150,
                calories=80,
                source='manual'
            )
            
            micros = {'vitamin_c': 10, 'potassium': 200}
            log.set_micros(micros)
            
            db.session.add(log)
            db.session.commit()
            
            assert log.get_micros() == micros


class TestFoodItem:
    
    def test_create_food_item(self, app):
        """Test food item creation."""
        with app.app_context():
            nutrition = {
                'calories_per_100g': 52,
                'protein_per_100g': 0.3,
                'carbs_per_100g': 14,
                'fat_per_100g': 0.2
            }
            
            item = FoodItem(
                canonical_name='Apple',
                source='openfoodfacts',
                brand='Generic'
            )
            item.set_nutrition(nutrition)
            
            db.session.add(item)
            db.session.commit()
            
            assert item.canonical_name == 'Apple'
            assert item.get_nutrition() == nutrition


class TestCoachMessage:
    
    def test_create_coach_message(self, app, user):
        """Test coach message creation."""
        with app.app_context():
            message = CoachMessage(
                user_id=user.id,
                role='user',
                content='What should I eat for breakfast?'
            )
            
            refs = [{'title': 'Healthy Breakfast Ideas', 'url': 'http://example.com'}]
            message.set_refs(refs)
            
            db.session.add(message)
            db.session.commit()
            
            assert message.content == 'What should I eat for breakfast?'
            assert message.role == 'user'
            assert message.get_refs() == refs


class TestWeighIn:
    
    def test_create_weigh_in(self, app, user):
        """Test weigh-in creation."""
        with app.app_context():
            weigh_in = WeighIn(
                user_id=user.id,
                weight_kg=75.5
            )
            
            db.session.add(weigh_in)
            db.session.commit()
            
            assert weigh_in.weight_kg == 75.5
            assert weigh_in.user_id == user.id
            assert isinstance(weigh_in.recorded_at, datetime)


class TestWaterIntake:
    
    def test_create_water_intake(self, app, user):
        """Test water intake creation."""
        with app.app_context():
            intake = WaterIntake(
                user_id=user.id,
                ml=500
            )
            
            db.session.add(intake)
            db.session.commit()
            
            assert intake.ml == 500
            assert intake.user_id == user.id
            assert isinstance(intake.recorded_at, datetime)


class TestPhoto:
    
    def test_create_photo(self, app, user):
        """Test photo creation."""
        with app.app_context():
            photo = Photo(
                user_id=user.id,
                filepath='/uploads/test.jpg'
            )
            
            analysis = {'candidates': [{'name': 'apple', 'confidence': 0.9}]}
            photo.set_analysis(analysis)
            
            db.session.add(photo)
            db.session.commit()
            
            assert photo.filepath == '/uploads/test.jpg'
            assert photo.get_analysis() == analysis