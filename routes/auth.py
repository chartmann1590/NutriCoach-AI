from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Profile, Settings
from forms.auth import LoginForm, RegistrationForm
from extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            
            # Check if user needs onboarding
            if not user.profile:
                return redirect(url_for('onboarding.step1'))
            
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Create default settings
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
            db.session.commit()
            
            login_user(user, remember=True)
            flash('Registration successful! Let\'s set up your profile.', 'success')
            return redirect(url_for('onboarding.step1'))
        
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))