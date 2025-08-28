from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import Settings, Profile
from forms.settings import OllamaSettingsForm
from services.ollama_client import OllamaClient
from extensions import db

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/')
@login_required
def index():
    """Settings overview page"""
    settings = Settings.query.filter_by(user_id=current_user.id).first()
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    
    return render_template('settings/index.html', 
                         settings=settings, 
                         profile=profile)


@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Edit profile settings"""
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    
    if not profile:
        flash('Please complete onboarding first.', 'warning')
        return redirect(url_for('onboarding.step1'))
    
    if request.method == 'POST':
        try:
            # Update basic info
            profile.name = request.form.get('name', profile.name)
            profile.age = int(request.form.get('age', profile.age))
            profile.sex = request.form.get('sex', profile.sex)
            profile.height_cm = float(request.form.get('height_cm', profile.height_cm))
            profile.weight_kg = float(request.form.get('weight_kg', profile.weight_kg))
            
            # Update goals
            profile.activity_level = request.form.get('activity_level', profile.activity_level)
            profile.goal_type = request.form.get('goal_type', profile.goal_type)
            profile.target_weight_kg = float(request.form.get('target_weight_kg', 0)) or None
            profile.timeframe_weeks = int(request.form.get('timeframe_weeks', 0)) or None
            
            # Update lifestyle
            profile.budget_range = request.form.get('budget_range', profile.budget_range)
            profile.cooking_skill = request.form.get('cooking_skill', profile.cooking_skill)
            profile.meals_per_day = int(request.form.get('meals_per_day', profile.meals_per_day))
            profile.sleep_schedule = request.form.get('sleep_schedule', profile.sleep_schedule)
            
            # Update preferences (checkboxes)
            preferences = request.form.getlist('preferences')
            # Handle allergies as comma-separated text
            allergies_text = request.form.get('allergies_text', '').strip()
            allergies = [a.strip() for a in allergies_text.split(',') if a.strip()] if allergies_text else []
            equipment = request.form.getlist('equipment')
            conditions = request.form.get('conditions', '').strip()
            
            profile.set_preferences(preferences)
            profile.set_allergies(allergies)
            profile.set_equipment(equipment)
            profile.set_conditions([conditions] if conditions else [])
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please check your input.', 'error')
    
    return render_template('settings/profile.html', profile=profile)


@settings_bp.route('/ollama', methods=['GET', 'POST'])
@login_required
def ollama():
    """Ollama/AI settings"""
    settings = Settings.query.filter_by(user_id=current_user.id).first()
    
    if not settings:
        # Create default settings
        settings = Settings(
            user_id=current_user.id,
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
        db.session.commit()
    
    # Get available models
    available_models = []
    connection_status = False
    
    try:
        # Use the settings URL directly for testing connection
        client = OllamaClient(settings.ollama_url)
        connection_status = client.test_connection()
        
        if connection_status:
            models_data = client.list_models()
            available_models = [model['name'] for model in models_data] if models_data else []
            
            # Update last sync time
            settings.last_model_sync_at = db.func.now()
            db.session.commit()
            
    except Exception as e:
        flash(f'Error connecting to Ollama: {str(e)}', 'error')
    
    # Create form with available models
    form = OllamaSettingsForm()
    form.chat_model.choices = [('', 'Select a model...')] + [(model, model) for model in available_models]
    form.vision_model.choices = [('', 'Select a model...')] + [(model, model) for model in available_models]
    
    if form.validate_on_submit():
        try:
            settings.ollama_url = form.ollama_url.data
            settings.chat_model = form.chat_model.data if form.chat_model.data else None
            settings.vision_model = form.vision_model.data if form.vision_model.data else None
            settings.system_prompt = form.system_prompt.data
            settings.safety_mode = form.safety_mode.data
            
            db.session.commit()
            flash('Ollama settings updated successfully!', 'success')
            return redirect(url_for('settings.ollama'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating settings. Please try again.', 'error')
    
    # Populate form with current settings
    if request.method == 'GET':
        form.ollama_url.data = settings.ollama_url
        form.chat_model.data = settings.chat_model
        form.vision_model.data = settings.vision_model
        form.system_prompt.data = settings.system_prompt
        form.safety_mode.data = settings.safety_mode
    
    return render_template('settings/ollama.html', 
                         form=form,
                         settings=settings,
                         available_models=available_models,
                         connection_status=connection_status)


@settings_bp.route('/test-connection', methods=['POST'])
@login_required
def test_connection():
    """Test Ollama connection via AJAX"""
    data = request.get_json()
    url = data.get('url', '')
    
    try:
        client = OllamaClient(url)
        connected = client.test_connection()
        
        models = []
        if connected:
            try:
                models = client.list_models()
            except:
                pass
        
        return jsonify({
            'connected': connected,
            'models': models
        })
    
    except Exception as e:
        return jsonify({
            'connected': False,
            'error': str(e)
        })


@settings_bp.route('/pull-model', methods=['POST'])
@login_required
def pull_model():
    """Pull a model from Ollama"""
    data = request.get_json()
    model_name = data.get('model', '')
    
    if not model_name:
        return jsonify({'error': 'Model name is required'}), 400
    
    try:
        client = OllamaClient.from_user_settings()
        
        success = client.pull_model(model_name)
        
        if success:
            return jsonify({'success': True, 'message': f'Model {model_name} pulled successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to pull model'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@settings_bp.route('/export')
@login_required
def export_data():
    """Data export settings"""
    return render_template('settings/export.html')


@settings_bp.route('/privacy')
@login_required
def privacy():
    """Privacy and data settings"""
    return render_template('settings/privacy.html')


@settings_bp.route('/account')
@login_required
def account():
    """Account settings"""
    return render_template('settings/account.html')