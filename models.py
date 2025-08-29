from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
import json


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    settings = db.relationship('Settings', backref='user', uselist=False, cascade='all, delete-orphan')
    food_logs = db.relationship('FoodLog', backref='user', cascade='all, delete-orphan')
    coach_messages = db.relationship('CoachMessage', backref='user', cascade='all, delete-orphan')
    photos = db.relationship('Photo', backref='user', cascade='all, delete-orphan')
    weigh_ins = db.relationship('WeighIn', backref='user', cascade='all, delete-orphan')
    water_intakes = db.relationship('WaterIntake', backref='user', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', backref='user', cascade='all, delete-orphan')
    created_notifications = db.relationship('Notification', foreign_keys='Notification.created_by', backref='creator')
    notification_templates = db.relationship('NotificationTemplate', backref='creator', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Basic info
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)  # male, female, other
    height_cm = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    
    # Goals
    activity_level = db.Column(db.String(20), nullable=False)  # sedentary, light, moderate, active, very_active
    goal_type = db.Column(db.String(20), nullable=False)  # lose, maintain, gain
    target_weight_kg = db.Column(db.Float)
    timeframe_weeks = db.Column(db.Integer)
    
    # Preferences (stored as JSON)
    preferences = db.Column(db.Text)  # dietary preferences
    allergies = db.Column(db.Text)  # allergies list
    conditions = db.Column(db.Text)  # medical conditions
    
    # Lifestyle
    budget_range = db.Column(db.String(20))  # low, medium, high
    cooking_skill = db.Column(db.String(20))  # beginner, intermediate, advanced
    equipment = db.Column(db.Text)  # available kitchen equipment
    meals_per_day = db.Column(db.Integer, default=3)
    sleep_schedule = db.Column(db.String(50))  # early_bird, night_owl, flexible
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_preferences(self):
        return json.loads(self.preferences) if self.preferences else []
    
    def set_preferences(self, prefs):
        self.preferences = json.dumps(prefs)
    
    def get_allergies(self):
        return json.loads(self.allergies) if self.allergies else []
    
    def set_allergies(self, allergies):
        self.allergies = json.dumps(allergies)
    
    def get_conditions(self):
        return json.loads(self.conditions) if self.conditions else []
    
    def set_conditions(self, conditions):
        self.conditions = json.dumps(conditions)
    
    def get_equipment(self):
        return json.loads(self.equipment) if self.equipment else []
    
    def set_equipment(self, equipment):
        self.equipment = json.dumps(equipment)


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Ollama configuration
    ollama_url = db.Column(db.String(255), default='http://localhost:11434')
    chat_model = db.Column(db.String(100))
    vision_model = db.Column(db.String(100))
    system_prompt = db.Column(db.Text)
    last_model_sync_at = db.Column(db.DateTime)
    
    # AI behavior
    safety_mode = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canonical_name = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String(50), nullable=False)  # openfoodfacts, wikipedia, manual
    brand = db.Column(db.String(100))
    barcode = db.Column(db.String(50))
    nutrition = db.Column(db.Text)  # JSON nutrition data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    food_logs = db.relationship('FoodLog', backref='food_item')
    
    def get_nutrition(self):
        return json.loads(self.nutrition) if self.nutrition else {}
    
    def set_nutrition(self, nutrition_data):
        self.nutrition = json.dumps(nutrition_data)


class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'))
    
    # Food details
    custom_name = db.Column(db.String(200))  # if not using food_item
    meal = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    grams = db.Column(db.Float, nullable=False)
    
    # Nutritional data
    calories = db.Column(db.Float, nullable=False)
    protein_g = db.Column(db.Float, default=0)
    carbs_g = db.Column(db.Float, default=0)
    fat_g = db.Column(db.Float, default=0)
    fiber_g = db.Column(db.Float, default=0)
    sugar_g = db.Column(db.Float, default=0)
    sodium_mg = db.Column(db.Float, default=0)
    micros = db.Column(db.Text)  # JSON for micronutrients
    
    # Metadata
    source = db.Column(db.String(20), nullable=False)  # manual, vision, barcode
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_micros(self):
        return json.loads(self.micros) if self.micros else {}
    
    def set_micros(self, micros_data):
        self.micros = json.dumps(micros_data)


class CoachMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # system, user, assistant
    content = db.Column(db.Text, nullable=False)
    refs = db.Column(db.Text)  # JSON references to sources
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_refs(self):
        return json.loads(self.refs) if self.refs else []
    
    def set_refs(self, refs_data):
        self.refs = json.dumps(refs_data)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    analysis = db.Column(db.Text)  # JSON analysis results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_analysis(self):
        return json.loads(self.analysis) if self.analysis else {}
    
    def set_analysis(self, analysis_data):
        self.analysis = json.dumps(analysis_data)


class WeighIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)


class WaterIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ml = db.Column(db.Integer, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)


class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)  # info, warning, error, critical
    action = db.Column(db.String(100), nullable=False)  # user_created, settings_changed, etc.
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # nullable for system actions
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # admin who performed action
    ip_address = db.Column(db.String(45))  # supports IPv6
    user_agent = db.Column(db.Text)
    extra_data = db.Column(db.Text)  # JSON for additional data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_metadata(self):
        return json.loads(self.extra_data) if self.extra_data else {}
    
    def set_metadata(self, data):
        self.extra_data = json.dumps(data) if data else None


class GlobalSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')  # general, ollama, security, etc.
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_value(self):
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value
    
    def set_value(self, value):
        if isinstance(value, (dict, list)):
            self.value = json.dumps(value)
        else:
            self.value = str(value)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Notification content
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'action', 'reminder', 'admin', 'system'
    category = db.Column(db.String(50))  # 'meal_reminder', 'food_logged', 'admin_message', 'goal_achieved', etc.
    
    # Notification state
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    is_dismissed = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.String(20), default='normal')  # 'low', 'normal', 'high', 'urgent'
    
    # Metadata
    action_url = db.Column(db.String(500))  # Optional URL for click action
    action_data = db.Column(db.Text)  # JSON data for custom actions
    expires_at = db.Column(db.DateTime)  # Optional expiration
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    read_at = db.Column(db.DateTime)
    dismissed_at = db.Column(db.DateTime)
    
    # Admin/system fields
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # For admin-created notifications
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    def dismiss(self):
        """Dismiss notification"""
        if not self.is_dismissed:
            self.is_dismissed = True
            self.dismissed_at = datetime.utcnow()
    
    def get_action_data(self):
        """Get action data as Python object"""
        if self.action_data:
            try:
                return json.loads(self.action_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_action_data(self, data):
        """Set action data from Python object"""
        if data:
            self.action_data = json.dumps(data)
        else:
            self.action_data = None
    
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def to_dict(self):
        """Convert notification to dictionary for JSON responses"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.notification_type,
            'category': self.category,
            'is_read': self.is_read,
            'is_dismissed': self.is_dismissed,
            'priority': self.priority,
            'action_url': self.action_url,
            'action_data': self.get_action_data(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired()
        }
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.title} ({self.notification_type})>'


class NotificationTemplate(db.Model):
    """Template for automatic notifications and admin quick-send"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Template content
    title_template = db.Column(db.String(200), nullable=False)
    message_template = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), default='normal')
    
    # Template settings
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_system_template = db.Column(db.Boolean, default=False)  # System vs user-created
    
    # Auto-reminder settings
    trigger_condition = db.Column(db.String(100))  # 'meal_reminder', 'goal_missed', etc.
    schedule_pattern = db.Column(db.String(100))  # Cron-like pattern for scheduling
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def render_title(self, user=None, **kwargs):
        """Render title template with user data"""
        template_vars = kwargs.copy()
        if user:
            template_vars.update({
                'user_name': user.profile.name if user.profile else user.username,
                'username': user.username
            })
        
        try:
            return self.title_template.format(**template_vars)
        except KeyError:
            return self.title_template
    
    def render_message(self, user=None, **kwargs):
        """Render message template with user data"""
        template_vars = kwargs.copy()
        if user:
            template_vars.update({
                'user_name': user.profile.name if user.profile else user.username,
                'username': user.username
            })
        
        try:
            return self.message_template.format(**template_vars)
        except KeyError:
            return self.message_template
    
    def __repr__(self):
        return f'<NotificationTemplate {self.name} ({self.notification_type})>'