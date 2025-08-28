from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from models import Profile
from services.recommendations import RecommendationService
from services.analytics import AnalyticsService
from forms.settings import FoodLogForm, WeighInForm, WaterIntakeForm

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        if not current_user.profile:
            return redirect(url_for('onboarding.step1'))
        return redirect(url_for('main.dashboard'))
    
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    if not current_user.profile:
        return redirect(url_for('onboarding.step1'))
    
    try:
        recommendations = RecommendationService()
        analytics = AnalyticsService()
        
        # Get today's summary
        today_summary = recommendations.get_daily_summary(current_user.id)
        
        # Get weekly summary
        weekly_summary = recommendations.get_weekly_summary(current_user.id)
        
        # Get quick stats
        streaks = analytics.get_logging_streaks(current_user.id)
        
        # Get recent food logs (last 5)
        recent_logs = analytics.export_data(
            current_user.id, 
            datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
            datetime.utcnow()
        )[-5:]
        
        context = {
            'today': today_summary,
            'weekly': weekly_summary,
            'streaks': streaks,
            'recent_logs': recent_logs,
            'user_name': current_user.profile.name if current_user.profile else current_user.username
        }
        
        return render_template('dashboard.html', **context)
    
    except Exception as e:
        print(f"Dashboard error: {e}")  # Debug print
        # Return a simple dashboard with minimal data that matches expected structure
        context = {
            'today': {
                'totals': {
                    'calories': 0,
                    'protein_g': 0,
                    'carbs_g': 0,
                    'fat_g': 0,
                    'fiber_g': 0,
                    'sugar_g': 0,
                    'sodium_mg': 0,
                    'calories_percent': 0,
                    'protein_percent': 0,
                    'carbs_percent': 0,
                    'fat_percent': 0,
                    'meal_breakdown': {
                        'breakfast': {'calories': 0, 'count': 0},
                        'lunch': {'calories': 0, 'count': 0},
                        'dinner': {'calories': 0, 'count': 0},
                        'snack': {'calories': 0, 'count': 0}
                    }
                },
                'targets': {
                    'calories': 2000,
                    'protein_g': 150,
                    'carbs_g': 250,
                    'fat_g': 67
                },
                'remaining': {
                    'calories': 2000,
                    'protein_g': 150,
                    'carbs_g': 250,
                    'fat_g': 67
                }
            },
            'weekly': {
                'days_logged': 0,
                'averages': {
                    'calories': 0,
                    'protein_g': 0,
                    'carbs_g': 0,
                    'fat_g': 0
                }
            },
            'streaks': {
                'current_streak': 0,
                'longest_streak': 0,
                'total_days_logged': 0
            },
            'recent_logs': [],
            'user_name': current_user.profile.name if current_user.profile else current_user.username,
            'error': str(e)
        }
        return render_template('dashboard.html', **context)


@main_bp.route('/log')
@login_required
def log_food():
    """Food logging page"""
    if not current_user.profile:
        return redirect(url_for('onboarding.step1'))
    
    form = FoodLogForm()
    
    # Pre-fill form with URL parameters from search results
    if request.args.get('name'):
        form.custom_name.data = request.args.get('name')
    if request.args.get('calories'):
        form.calories.data = float(request.args.get('calories'))
    if request.args.get('protein'):
        form.protein_g.data = float(request.args.get('protein'))
    if request.args.get('carbs'):
        form.carbs_g.data = float(request.args.get('carbs'))
    if request.args.get('fat'):
        form.fat_g.data = float(request.args.get('fat'))
    # Set default amount to 100g since nutrition values are per 100g
    if not form.grams.data and request.args.get('calories'):
        form.grams.data = 100
    
    return render_template('log_food.html', form=form)


@main_bp.route('/search')
@login_required
def search_nutrition():
    """Nutrition search page"""
    if not current_user.profile:
        return redirect(url_for('onboarding.step1'))
    
    return render_template('search.html')


@main_bp.route('/progress')
@login_required
def progress():
    """Progress and analytics page"""
    if not current_user.profile:
        return redirect(url_for('onboarding.step1'))
    
    try:
        from datetime import datetime, timedelta
        
        analytics = AnalyticsService()
        recommendations = RecommendationService()
        
        # Get various analytics
        weight_trends = analytics.get_weight_trends(current_user.id, 90)
        nutrition_trends = analytics.get_nutrition_trends(current_user.id, 30)
        meal_distribution = analytics.get_meal_distribution(current_user.id, 30)
        macro_distribution = analytics.get_macro_distribution(current_user.id, 30)
        top_foods = analytics.get_top_foods(current_user.id, 30, 10)
        streaks = analytics.get_logging_streaks(current_user.id)
        insights = recommendations.get_progress_insights(current_user.id)
        
        # Calculate date ranges for export links
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        
        context = {
            'weight_trends': weight_trends,
            'nutrition_trends': nutrition_trends,
            'meal_distribution': meal_distribution,
            'macro_distribution': macro_distribution,
            'top_foods': top_foods,
            'streaks': streaks,
            'insights': insights,
            'export_from_date': thirty_days_ago.strftime('%Y-%m-%d'),
            'export_to_date': today.strftime('%Y-%m-%d')
        }
        
        return render_template('progress.html', **context)
    
    except Exception as e:
        from datetime import datetime, timedelta
        
        # Calculate date ranges for export links even in error case
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        
        # Provide default values to prevent template errors
        default_context = {
            'weight_trends': [],
            'nutrition_trends': [],
            'meal_distribution': {},
            'macro_distribution': {},
            'top_foods': [],
            'streaks': {
                'current_streak': 0,
                'total_days_logged': 0,
                'longest_streak': 0
            },
            'insights': [],
            'export_from_date': thirty_days_ago.strftime('%Y-%m-%d'),
            'export_to_date': today.strftime('%Y-%m-%d'),
            'error': str(e)
        }
        return render_template('progress.html', **default_context)


@main_bp.route('/quick-log')
@login_required
def quick_log():
    """Quick logging modal/page"""
    weigh_in_form = WeighInForm()
    water_form = WaterIntakeForm()
    
    return render_template('quick_log.html', 
                         weigh_in_form=weigh_in_form, 
                         water_form=water_form)


@main_bp.route('/photo-upload')
@login_required
def photo_upload():
    """Photo upload page"""
    if not current_user.profile:
        return redirect(url_for('onboarding.step1'))
    
    return render_template('photo_upload.html')


@main_bp.route('/disclaimer')
def disclaimer():
    """Medical disclaimer page"""
    return render_template('disclaimer.html')


@main_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')


@main_bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')


@main_bp.route('/help')
def help_center():
    """Help center page"""
    return render_template('help.html')