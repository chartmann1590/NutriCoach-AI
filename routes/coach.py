from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from models import CoachMessage, Settings
from services.recommendations import RecommendationService

coach_bp = Blueprint('coach', __name__)


@coach_bp.route('/')
@login_required
def index():
    """AI Coach chat interface"""
    if not current_user.profile:
        return redirect(url_for('onboarding.step1'))
    
    # Get recent chat messages
    messages = CoachMessage.query.filter_by(user_id=current_user.id)\
        .order_by(CoachMessage.created_at.desc())\
        .limit(50).all()
    
    messages = list(reversed(messages))  # Show oldest first
    
    # Get user settings to check if Ollama is configured
    settings = Settings.query.filter_by(user_id=current_user.id).first()
    ollama_configured = settings and settings.chat_model
    
    # Get quick action suggestions
    recommendations = RecommendationService()
    today_summary = recommendations.get_daily_summary(current_user.id)
    suggestions = recommendations.get_food_suggestions(
        current_user.id, 
        remaining_calories=today_summary['remaining']['calories']
    )
    
    return render_template('coach/index.html', 
                         messages=messages,
                         ollama_configured=ollama_configured,
                         today_summary=today_summary,
                         suggestions=suggestions)


@coach_bp.route('/quick-actions')
@login_required
def quick_actions():
    """Get quick action suggestions"""
    try:
        recommendations = RecommendationService()
        
        # Get current status
        today_summary = recommendations.get_daily_summary(current_user.id)
        weekly_summary = recommendations.get_weekly_summary(current_user.id)
        insights = recommendations.get_progress_insights(current_user.id)
        
        # Generate context-aware suggestions
        suggestions = []
        
        # Time-based suggestions
        from datetime import datetime
        hour = datetime.now().hour
        
        if 6 <= hour < 10:
            suggestions.append({
                'type': 'meal_plan',
                'title': 'Generate breakfast ideas',
                'description': 'Get healthy breakfast suggestions based on your goals',
                'prompt': f"I need breakfast ideas. I have {today_summary['remaining']['calories']:.0f} calories remaining for today."
            })
        elif 11 <= hour < 14:
            suggestions.append({
                'type': 'meal_plan',
                'title': 'Lunch recommendations',
                'description': 'Find nutritious lunch options',
                'prompt': f"Suggest a healthy lunch. I have {today_summary['remaining']['calories']:.0f} calories left for today."
            })
        elif 17 <= hour < 21:
            suggestions.append({
                'type': 'meal_plan',
                'title': 'Dinner planning',
                'description': 'Plan a balanced dinner',
                'prompt': f"Help me plan dinner. I have {today_summary['remaining']['calories']:.0f} calories remaining."
            })
        
        # Goal-based suggestions
        if today_summary['totals']['protein_percent'] < 80:
            suggestions.append({
                'type': 'nutrition',
                'title': 'Boost protein intake',
                'description': 'Get protein-rich food suggestions',
                'prompt': f"I'm only at {today_summary['totals']['protein_percent']:.0f}% of my protein goal. Suggest high-protein foods."
            })
        
        if today_summary['remaining']['calories'] > 500:
            suggestions.append({
                'type': 'meal_plan',
                'title': 'Plan remaining meals',
                'description': 'Distribute remaining calories across meals',
                'prompt': f"I have {today_summary['remaining']['calories']:.0f} calories left today. Help me plan my remaining meals."
            })
        
        # Weekly insights
        if weekly_summary['days_logged'] < 5:
            suggestions.append({
                'type': 'habit',
                'title': 'Improve logging consistency',
                'description': 'Tips for consistent food tracking',
                'prompt': f"I've only logged {weekly_summary['days_logged']} days this week. How can I be more consistent with tracking?"
            })
        
        # Add general suggestions
        suggestions.extend([
            {
                'type': 'meal_plan',
                'title': 'Weekly meal prep',
                'description': 'Plan meals for the upcoming week',
                'prompt': 'Help me create a 7-day meal plan based on my goals and preferences.'
            },
            {
                'type': 'shopping',
                'title': 'Grocery list',
                'description': 'Generate a shopping list for healthy eating',
                'prompt': 'Create a grocery shopping list based on my nutritional needs and dietary preferences.'
            },
            {
                'type': 'analysis',
                'title': 'Analyze my progress',
                'description': 'Review recent nutrition data and provide insights',
                'prompt': 'Analyze my recent eating patterns and give me feedback on my progress toward my goals.'
            },
            {
                'type': 'education',
                'title': 'Nutrition education',
                'description': 'Learn about macronutrients and healthy eating',
                'prompt': 'Explain the role of macronutrients in my diet and how to balance them for my goals.'
            }
        ])
        
        return jsonify({'suggestions': suggestions[:8]})  # Limit to 8 suggestions
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@coach_bp.route('/conversation-starters')
@login_required
def conversation_starters():
    """Get conversation starter suggestions"""
    try:
        profile = current_user.profile
        
        starters = [
            "What should I eat for my next meal?",
            "How am I doing with my nutrition goals?",
            "I'm craving something sweet. What are healthy alternatives?",
            "Can you suggest a pre-workout snack?",
            "Help me understand my macro balance.",
            "What foods are good for my fitness goals?",
            "I'm eating out tonight. Any recommendations?",
            "How can I meal prep for the week?",
        ]
        
        # Personalize based on user's goal
        if profile and profile.goal_type == 'lose':
            starters.extend([
                "What are some low-calorie filling foods?",
                "How can I create a calorie deficit without feeling hungry?",
            ])
        elif profile and profile.goal_type == 'gain':
            starters.extend([
                "What are healthy high-calorie foods for weight gain?",
                "How can I increase my calorie intake healthily?",
            ])
        
        # Personalize based on dietary preferences
        if profile:
            preferences = profile.get_preferences()
            if 'vegetarian' in preferences:
                starters.append("What are good vegetarian protein sources?")
            if 'vegan' in preferences:
                starters.append("Help me get enough protein on a vegan diet.")
            if 'keto' in preferences:
                starters.append("What are keto-friendly meal ideas?")
        
        return jsonify({'starters': starters})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500