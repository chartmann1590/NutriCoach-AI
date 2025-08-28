from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from models import Profile, Settings
from forms.onboarding import BasicInfoForm, GoalsForm, LifestyleForm, OllamaSettingsForm
from services.ollama_client import OllamaClient
from extensions import db

onboarding_bp = Blueprint('onboarding', __name__)


@onboarding_bp.route('/step1', methods=['GET', 'POST'])
@login_required
def step1():
    """Step 1: Basic Information"""
    if current_user.profile:
        return redirect(url_for('main.dashboard'))
    
    form = BasicInfoForm()
    
    if form.validate_on_submit():
        # Store form data in session
        session['onboarding_step1'] = {
            'name': form.name.data,
            'age': form.age.data,
            'sex': form.sex.data,
            'height_cm': form.height_cm.data,
            'weight_kg': form.weight_kg.data
        }
        return redirect(url_for('onboarding.step2'))
    
    # Pre-populate form from session if available
    if 'onboarding_step1' in session:
        data = session['onboarding_step1']
        form.name.data = data.get('name')
        form.age.data = data.get('age')
        form.sex.data = data.get('sex')
        form.height_cm.data = data.get('height_cm')
        form.weight_kg.data = data.get('weight_kg')
    
    return render_template('onboarding/step1.html', form=form, step=1, total_steps=4)


@onboarding_bp.route('/step2', methods=['GET', 'POST'])
@login_required
def step2():
    """Step 2: Goals"""
    if current_user.profile:
        return redirect(url_for('main.dashboard'))
    
    if 'onboarding_step1' not in session:
        flash('Please complete the previous step first.', 'warning')
        return redirect(url_for('onboarding.step1'))
    
    form = GoalsForm()
    
    if form.validate_on_submit():
        session['onboarding_step2'] = {
            'activity_level': form.activity_level.data,
            'goal_type': form.goal_type.data,
            'target_weight_kg': form.target_weight_kg.data,
            'timeframe_weeks': form.timeframe_weeks.data
        }
        return redirect(url_for('onboarding.step3'))
    
    # Pre-populate form from session if available
    if 'onboarding_step2' in session:
        data = session['onboarding_step2']
        form.activity_level.data = data.get('activity_level')
        form.goal_type.data = data.get('goal_type')
        form.target_weight_kg.data = data.get('target_weight_kg')
        form.timeframe_weeks.data = data.get('timeframe_weeks')
    
    return render_template('onboarding/step2.html', form=form, step=2, total_steps=4)


@onboarding_bp.route('/step3', methods=['GET', 'POST'])
@login_required
def step3():
    """Step 3: Lifestyle & Preferences"""
    if current_user.profile:
        return redirect(url_for('main.dashboard'))
    
    if 'onboarding_step2' not in session:
        flash('Please complete the previous steps first.', 'warning')
        return redirect(url_for('onboarding.step1'))
    
    form = LifestyleForm()
    
    if form.validate_on_submit():
        session['onboarding_step3'] = {
            'preferences': form.preferences.data,
            'allergies': form.allergies.data,
            'conditions': form.conditions.data,
            'budget_range': form.budget_range.data,
            'cooking_skill': form.cooking_skill.data,
            'equipment': form.equipment.data,
            'meals_per_day': int(form.meals_per_day.data),
            'sleep_schedule': form.sleep_schedule.data
        }
        return redirect(url_for('onboarding.step4'))
    
    # Pre-populate form from session if available
    if 'onboarding_step3' in session:
        data = session['onboarding_step3']
        form.preferences.data = data.get('preferences', [])
        form.allergies.data = data.get('allergies', [])
        form.conditions.data = data.get('conditions')
        form.budget_range.data = data.get('budget_range')
        form.cooking_skill.data = data.get('cooking_skill')
        form.equipment.data = data.get('equipment', [])
        form.meals_per_day.data = str(data.get('meals_per_day', 3))
        form.sleep_schedule.data = data.get('sleep_schedule')
    
    return render_template('onboarding/step3.html', form=form, step=3, total_steps=4)


@onboarding_bp.route('/step4', methods=['GET', 'POST'])
@login_required
def step4():
    """Step 4: Ollama Settings"""
    if current_user.profile:
        return redirect(url_for('main.dashboard'))
    
    if 'onboarding_step3' not in session:
        flash('Please complete the previous steps first.', 'warning')
        return redirect(url_for('onboarding.step1'))
    
    form = OllamaSettingsForm()
    
    # Get available models if Ollama URL is provided
    available_models = []
    if request.method == 'GET' or form.ollama_url.data:
        try:
            # During onboarding, we test the provided URL
            client = OllamaClient(form.ollama_url.data or 'http://localhost:11434')
            if client.test_connection():
                models = client.list_models()
                available_models = [(model['name'], model['name']) for model in models]
        except:
            pass
    
    if form.validate_on_submit():
        try:
            # Create profile with all the collected data
            step1_data = session['onboarding_step1']
            step2_data = session['onboarding_step2']
            step3_data = session['onboarding_step3']
            
            profile = Profile(
                user_id=current_user.id,
                **step1_data,
                **step2_data,
                budget_range=step3_data['budget_range'],
                cooking_skill=step3_data['cooking_skill'],
                meals_per_day=step3_data['meals_per_day'],
                sleep_schedule=step3_data['sleep_schedule']
            )
            
            # Set JSON fields
            profile.set_preferences(step3_data['preferences'])
            profile.set_allergies(step3_data['allergies'])
            profile.set_conditions([step3_data['conditions']] if step3_data['conditions'] else [])
            profile.set_equipment(step3_data['equipment'])
            
            db.session.add(profile)
            
            # Update settings with Ollama configuration
            settings = Settings.query.filter_by(user_id=current_user.id).first()
            if settings:
                settings.ollama_url = form.ollama_url.data
                # Set default models if available
                if available_models:
                    # Prefer chat models
                    chat_models = [m for m in available_models if 'llama' in m[0].lower() or 'mistral' in m[0].lower()]
                    if chat_models:
                        settings.chat_model = chat_models[0][0]
                    
                    # Prefer vision models
                    vision_models = [m for m in available_models if 'llava' in m[0].lower() or 'vision' in m[0].lower()]
                    if vision_models:
                        settings.vision_model = vision_models[0][0]
            
            db.session.commit()
            
            # Clear onboarding session data
            for key in ['onboarding_step1', 'onboarding_step2', 'onboarding_step3']:
                session.pop(key, None)
            
            flash('Welcome to NutriCoach! Your profile has been set up successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        
        except Exception as e:
            db.session.rollback()
            flash('There was an error setting up your profile. Please try again.', 'error')
    
    return render_template('onboarding/step4.html', 
                         form=form, 
                         step=4, 
                         total_steps=4,
                         available_models=available_models)


@onboarding_bp.route('/skip')
@login_required
def skip_onboarding():
    """Skip onboarding with minimal profile"""
    if current_user.profile:
        return redirect(url_for('main.dashboard'))
    
    try:
        # Create minimal profile
        profile = Profile(
            user_id=current_user.id,
            name=current_user.username,
            age=25,
            sex='other',
            height_cm=170,
            weight_kg=70,
            activity_level='moderate',
            goal_type='maintain',
            budget_range='medium',
            cooking_skill='intermediate',
            meals_per_day=3,
            sleep_schedule='flexible'
        )
        
        profile.set_preferences(['omnivore'])
        profile.set_allergies([])
        profile.set_conditions([])
        profile.set_equipment(['stove', 'oven', 'microwave'])
        
        db.session.add(profile)
        db.session.commit()
        
        # Clear any onboarding session data
        for key in ['onboarding_step1', 'onboarding_step2', 'onboarding_step3']:
            session.pop(key, None)
        
        flash('Profile created with default settings. You can update it later in Settings.', 'info')
        return redirect(url_for('main.dashboard'))
    
    except Exception as e:
        db.session.rollback()
        flash('Error creating profile. Please try the full onboarding process.', 'error')
        return redirect(url_for('onboarding.step1'))