from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, SelectMultipleField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class BasicInfoForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=13, max=120)])
    sex = SelectField('Sex', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    height_cm = FloatField('Height (cm)', validators=[DataRequired(), NumberRange(min=100, max=250)])
    weight_kg = FloatField('Current Weight (kg)', validators=[DataRequired(), NumberRange(min=30, max=300)])
    submit = SubmitField('Next')


class GoalsForm(FlaskForm):
    activity_level = SelectField('Activity Level', choices=[
        ('sedentary', 'Sedentary (little/no exercise)'),
        ('light', 'Light (light exercise/sports 1-3 days/week)'),
        ('moderate', 'Moderate (moderate exercise/sports 3-5 days/week)'),
        ('active', 'Active (hard exercise/sports 6-7 days a week)'),
        ('very_active', 'Very Active (very hard exercise & physical job)')
    ], validators=[DataRequired()])
    
    goal_type = SelectField('Primary Goal', choices=[
        ('lose', 'Lose Weight'),
        ('maintain', 'Maintain Weight'),
        ('gain', 'Gain Weight')
    ], validators=[DataRequired()])
    
    target_weight_kg = FloatField('Target Weight (kg)', validators=[Optional(), NumberRange(min=30, max=300)])
    timeframe_weeks = IntegerField('Timeframe (weeks)', validators=[Optional(), NumberRange(min=1, max=104)])
    submit = SubmitField('Next')


class LifestyleForm(FlaskForm):
    preferences = SelectMultipleField('Dietary Preferences', choices=[
        ('omnivore', 'Omnivore'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('kosher', 'Kosher'),
        ('halal', 'Halal'),
        ('keto', 'Ketogenic'),
        ('paleo', 'Paleo'),
        ('mediterranean', 'Mediterranean')
    ])
    
    allergies = SelectMultipleField('Allergies', choices=[
        ('nuts', 'Tree Nuts'),
        ('peanuts', 'Peanuts'),
        ('dairy', 'Dairy'),
        ('eggs', 'Eggs'),
        ('soy', 'Soy'),
        ('gluten', 'Gluten'),
        ('shellfish', 'Shellfish'),
        ('fish', 'Fish')
    ])
    
    conditions = TextAreaField('Medical Considerations (Optional)')
    
    budget_range = SelectField('Budget Range', choices=[
        ('low', 'Low Budget'),
        ('medium', 'Medium Budget'),
        ('high', 'High Budget')
    ], validators=[DataRequired()])
    
    cooking_skill = SelectField('Cooking Skill', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], validators=[DataRequired()])
    
    equipment = SelectMultipleField('Available Equipment', choices=[
        ('stove', 'Stove'),
        ('oven', 'Oven'),
        ('microwave', 'Microwave'),
        ('blender', 'Blender'),
        ('air_fryer', 'Air Fryer'),
        ('slow_cooker', 'Slow Cooker'),
        ('pressure_cooker', 'Pressure Cooker'),
        ('food_processor', 'Food Processor')
    ])
    
    meals_per_day = SelectField('Meals Per Day', choices=[
        ('2', '2 meals'),
        ('3', '3 meals'),
        ('4', '4 meals'),
        ('5', '5 meals'),
        ('6', '6 meals')
    ], validators=[DataRequired()])
    
    sleep_schedule = SelectField('Sleep Schedule', choices=[
        ('early_bird', 'Early Bird (early to bed, early to rise)'),
        ('night_owl', 'Night Owl (late to bed, late to rise)'),
        ('flexible', 'Flexible')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Next')


class OllamaSettingsForm(FlaskForm):
    ollama_url = StringField('Ollama URL', validators=[DataRequired()], default='http://localhost:11434')
    submit = SubmitField('Complete Setup')