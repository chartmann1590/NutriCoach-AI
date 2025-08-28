from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, URL


class OllamaSettingsForm(FlaskForm):
    ollama_url = StringField('Ollama URL', validators=[DataRequired(), URL()], default='http://localhost:11434')
    chat_model = SelectField('Chat Model', choices=[])
    vision_model = SelectField('Vision Model', choices=[])
    system_prompt = TextAreaField('System Prompt')
    safety_mode = BooleanField('Enable Safety Mode')
    submit = SubmitField('Save Settings')


class FoodLogForm(FlaskForm):
    custom_name = StringField('Food Name', validators=[DataRequired()])
    meal = SelectField('Meal', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack')
    ], validators=[DataRequired()])
    grams = StringField('Amount (grams)', validators=[DataRequired()])
    calories = StringField('Calories', validators=[DataRequired()])
    protein_g = StringField('Protein (g)', default='0')
    carbs_g = StringField('Carbs (g)', default='0')
    fat_g = StringField('Fat (g)', default='0')
    fiber_g = StringField('Fiber (g)', default='0')
    sugar_g = StringField('Sugar (g)', default='0')
    sodium_mg = StringField('Sodium (mg)', default='0')
    submit = SubmitField('Log Food')


class WeighInForm(FlaskForm):
    weight_kg = StringField('Weight (kg)', validators=[DataRequired()])
    submit = SubmitField('Record Weight')


class WaterIntakeForm(FlaskForm):
    ml = StringField('Water (ml)', validators=[DataRequired()])
    submit = SubmitField('Log Water')