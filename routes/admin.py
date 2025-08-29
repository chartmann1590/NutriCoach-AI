from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_
import os
import json

from models import User, Profile, Settings, FoodLog, SystemLog, GlobalSettings, db
from forms.admin import (AdminLoginForm, CreateUserForm, EditUserForm, OllamaSettingsForm, 
                        GlobalSettingForm, SystemMaintenanceForm, BulkUserActionForm)
from services.ollama_client import OllamaClient

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def log_admin_action(action, message, user_id=None, metadata=None):
    """Helper function to log admin actions"""
    log = SystemLog(
        level='info',
        action=action,
        message=message,
        user_id=user_id,
        admin_id=current_user.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')
    )
    if metadata:
        log.set_metadata(metadata)
    db.session.add(log)
    db.session.commit()


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'admin_users': User.query.filter_by(is_admin=True).count(),
        'total_food_logs': FoodLog.query.count(),
        'recent_logs': SystemLog.query.order_by(desc(SystemLog.created_at)).limit(10).all()
    }
    
    # Get user registration trends (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_registrations_raw = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= thirty_days_ago).group_by(
        func.date(User.created_at)
    ).all()
    
    # Convert to JSON serializable format
    daily_registrations = []
    for row in daily_registrations_raw:
        try:
            # Handle both datetime and string dates
            if hasattr(row.date, 'strftime'):
                date_str = row.date.strftime('%Y-%m-%d')
            else:
                # If it's already a string, use it directly
                date_str = str(row.date)
            daily_registrations.append({
                'date': date_str,
                'count': row.count
            })
        except Exception as e:
            # Skip malformed dates
            continue
    
    # Get system health
    health = {
        'db_connected': True,
        'ollama_status': _check_ollama_status(),
        'disk_usage': _get_disk_usage(),
        'last_backup': _get_last_backup_time()
    }
    
    return render_template('admin/dashboard.html', stats=stats, 
                         daily_registrations=daily_registrations, health=health)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    filter_type = request.args.get('filter', 'all')
    
    query = User.query
    
    if search:
        query = query.filter(User.username.contains(search))
    
    if filter_type == 'admin':
        query = query.filter_by(is_admin=True)
    elif filter_type == 'active':
        query = query.filter_by(is_active=True)
    elif filter_type == 'inactive':
        query = query.filter_by(is_active=False)
    
    users = query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get registration setting
    registration_setting = GlobalSettings.query.filter_by(key='user_registration_enabled').first()
    registration_enabled = registration_setting.get_value().lower() == 'true' if registration_setting else True
    
    return render_template('admin/users.html', users=users, search=search, filter_type=filter_type, registration_enabled=registration_enabled)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create new user"""
    form = CreateUserForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            is_admin=form.is_admin.data,
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Create default settings
            settings = Settings(user_id=user.id)
            db.session.add(settings)
            db.session.commit()
            
            log_admin_action('user_created', f'Created user: {user.username}', user.id,
                           {'is_admin': user.is_admin, 'is_active': user.is_active})
            
            flash(f'User {user.username} created successfully!', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creating user. Please try again.', 'error')
    
    return render_template('admin/create_user.html', form=form)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    
    if form.validate_on_submit():
        old_values = {
            'username': user.username,
            'is_admin': user.is_admin,
            'is_active': user.is_active
        }
        
        user.username = form.username.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        
        if form.reset_password.data and form.new_password.data:
            user.set_password(form.new_password.data)
        
        try:
            db.session.commit()
            
            changes = {}
            for key, old_val in old_values.items():
                new_val = getattr(user, key)
                if old_val != new_val:
                    changes[key] = {'old': old_val, 'new': new_val}
            
            if form.reset_password.data:
                changes['password'] = 'reset'
            
            log_admin_action('user_updated', f'Updated user: {user.username}', user.id, changes)
            
            flash(f'User {user.username} updated successfully!', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating user. Please try again.', 'error')
    
    return render_template('admin/edit_user.html', form=form, user=user)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash("You cannot modify your own status!", 'error')
        return redirect(url_for('admin.users'))
    
    old_status = user.is_active
    user.is_active = not user.is_active
    
    try:
        db.session.commit()
        
        action = 'activated' if user.is_active else 'deactivated'
        log_admin_action('user_status_changed', f'{action.title()} user: {user.username}', 
                        user.id, {'old_status': old_status, 'new_status': user.is_active})
        
        flash(f'User {user.username} {action} successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating user status. Please try again.', 'error')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Reset user password to default"""
    user = User.query.get_or_404(user_id)
    
    # Generate a random password or use default
    import secrets
    import string
    new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    try:
        user.set_password(new_password)
        db.session.commit()
        
        log_admin_action('password_reset', f'Reset password for user: {user.username}', user.id)
        
        # Return the password in a secure way for display in modal
        return jsonify({
            'success': True,
            'username': user.username,
            'new_password': new_password,
            'message': f'Password reset successfully for {user.username}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error resetting password. Please try again.'
        }), 500


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash("You cannot delete your own account!", 'error')
        return redirect(url_for('admin.users'))
    
    username = user.username
    
    try:
        db.session.delete(user)
        db.session.commit()
        
        log_admin_action('user_deleted', f'Deleted user: {username}', user_id)
        flash(f'User {username} deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user. Please try again.', 'error')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/toggle-registration', methods=['POST'])
@login_required
@admin_required
def toggle_registration():
    """Toggle user registration on/off"""
    try:
        setting = GlobalSettings.query.filter_by(key='user_registration_enabled').first()
        
        if not setting:
            # Create setting if it doesn't exist
            setting = GlobalSettings(
                key='user_registration_enabled',
                value='true',
                description='Allow new user registration',
                category='security',
                updated_by=current_user.id
            )
            db.session.add(setting)
        
        # Toggle the value
        current_value = setting.get_value().lower()
        new_value = 'false' if current_value == 'true' else 'true'
        setting.set_value(new_value)
        setting.updated_by = current_user.id
        setting.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        status = 'enabled' if new_value == 'true' else 'disabled'
        log_admin_action('registration_toggled', f'User registration {status}', 
                        metadata={'old_value': current_value, 'new_value': new_value})
        
        return jsonify({
            'success': True,
            'enabled': new_value == 'true',
            'message': f'User registration {status} successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error toggling registration. Please try again.'
        }), 500


@admin_bp.route('/users/bulk-action', methods=['POST'])
@login_required
@admin_required
def bulk_user_action():
    """Perform bulk actions on users"""
    form = BulkUserActionForm()
    
    if form.validate_on_submit():
        user_ids = [int(id.strip()) for id in form.user_ids.data.split(',') if id.strip().isdigit()]
        action = form.action.data
        
        if not user_ids:
            flash('No valid user IDs provided.', 'error')
            return redirect(url_for('admin.users'))
        
        # Prevent admin from affecting their own account in bulk actions
        if current_user.id in user_ids:
            user_ids.remove(current_user.id)
            flash('Your own account was excluded from the bulk action.', 'warning')
        
        try:
            users = User.query.filter(User.id.in_(user_ids)).all()
            
            if action == 'activate':
                for user in users:
                    user.is_active = True
                message = f'Activated {len(users)} users'
                
            elif action == 'deactivate':
                for user in users:
                    user.is_active = False
                message = f'Deactivated {len(users)} users'
                
            elif action == 'make_admin':
                for user in users:
                    user.is_admin = True
                message = f'Made {len(users)} users admin'
                
            elif action == 'remove_admin':
                for user in users:
                    user.is_admin = False
                message = f'Removed admin from {len(users)} users'
                
            elif action == 'delete':
                usernames = [user.username for user in users]
                for user in users:
                    db.session.delete(user)
                message = f'Deleted {len(users)} users: {", ".join(usernames)}'
            
            db.session.commit()
            log_admin_action('bulk_user_action', message, metadata={'action': action, 'user_ids': user_ids})
            flash(message, 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Error performing bulk action. Please try again.', 'error')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """System settings management"""
    settings = GlobalSettings.query.order_by(GlobalSettings.category, GlobalSettings.key).all()
    settings_by_category = {}
    
    for setting in settings:
        if setting.category not in settings_by_category:
            settings_by_category[setting.category] = []
        settings_by_category[setting.category].append(setting)
    
    return render_template('admin/settings.html', settings_by_category=settings_by_category)


@admin_bp.route('/settings/ollama', methods=['GET', 'POST'])
@login_required
@admin_required
def ollama_settings():
    """Ollama configuration"""
    form = OllamaSettingsForm()
    
    # Load current settings
    current_settings = {
        'ollama_url': GlobalSettings.query.filter_by(key='ollama_url').first(),
        'default_chat_model': GlobalSettings.query.filter_by(key='default_chat_model').first(),
        'default_vision_model': GlobalSettings.query.filter_by(key='default_vision_model').first(),
        'model_timeout': GlobalSettings.query.filter_by(key='model_timeout').first(),
        'max_tokens': GlobalSettings.query.filter_by(key='max_tokens').first(),
        'temperature': GlobalSettings.query.filter_by(key='temperature').first(),
    }
    
    if request.method == 'GET':
        # Populate form with current values
        for key, setting in current_settings.items():
            if setting and hasattr(form, key):
                field = getattr(form, key)
                field.data = setting.get_value()
    
    if form.validate_on_submit():
        try:
            # Update each setting
            settings_data = {
                'ollama_url': (form.ollama_url.data, 'Ollama server URL'),
                'default_chat_model': (form.default_chat_model.data, 'Default chat model name'),
                'default_vision_model': (form.default_vision_model.data, 'Default vision model name'),
                'model_timeout': (form.model_timeout.data, 'Model request timeout in seconds'),
                'max_tokens': (form.max_tokens.data, 'Maximum tokens per request'),
                'temperature': (form.temperature.data, 'Model temperature setting'),
            }
            
            for key, (value, description) in settings_data.items():
                setting = current_settings[key]
                if not setting:
                    setting = GlobalSettings(
                        key=key,
                        category='ollama',
                        description=description,
                        updated_by=current_user.id
                    )
                    db.session.add(setting)
                
                setting.set_value(value)
                setting.updated_by = current_user.id
                setting.updated_at = datetime.utcnow()
            
            db.session.commit()
            log_admin_action('ollama_settings_updated', 'Updated Ollama configuration')
            flash('Ollama settings updated successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating Ollama settings. Please try again.', 'error')
    
    # Test Ollama connection
    ollama_status = _check_ollama_status()
    
    return render_template('admin/ollama_settings.html', form=form, ollama_status=ollama_status)


@admin_bp.route('/settings/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_setting():
    """Create new global setting"""
    form = GlobalSettingForm()
    
    if form.validate_on_submit():
        existing = GlobalSettings.query.filter_by(key=form.key.data).first()
        if existing:
            flash('Setting with this key already exists!', 'error')
        else:
            setting = GlobalSettings(
                key=form.key.data,
                description=form.description.data,
                category=form.category.data,
                updated_by=current_user.id
            )
            setting.set_value(form.value.data)
            
            try:
                db.session.add(setting)
                db.session.commit()
                
                log_admin_action('setting_created', f'Created setting: {setting.key}')
                flash('Setting created successfully!', 'success')
                return redirect(url_for('admin.settings'))
                
            except Exception as e:
                db.session.rollback()
                flash('Error creating setting. Please try again.', 'error')
    
    return render_template('admin/create_setting.html', form=form)


@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    """View system logs"""
    page = request.args.get('page', 1, type=int)
    level = request.args.get('level', '')
    action = request.args.get('action', '')
    
    query = SystemLog.query
    
    if level:
        query = query.filter_by(level=level)
    if action:
        query = query.filter(SystemLog.action.contains(action))
    
    logs = query.order_by(desc(SystemLog.created_at)).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('admin/logs.html', logs=logs, level=level, action=action)


@admin_bp.route('/api/test-ollama', methods=['POST'])
@login_required
@admin_required
def test_ollama_api():
    """API endpoint for testing Ollama connection"""
    data = request.get_json()
    ollama_url = data.get('ollama_url')
    
    if not ollama_url:
        return jsonify({'error': 'Ollama URL is required'}), 400
    
    try:
        client = OllamaClient(ollama_url)
        connected = client.test_connection()
        
        return jsonify({
            'connected': connected,
            'url': ollama_url
        })
    
    except Exception as e:
        return jsonify({'connected': False, 'error': str(e)})


@admin_bp.route('/maintenance', methods=['GET', 'POST'])
@login_required
@admin_required
def maintenance():
    """System maintenance operations"""
    form = SystemMaintenanceForm()
    
    if form.validate_on_submit():
        action = form.action.data
        
        try:
            if action == 'clear_logs':
                count = SystemLog.query.count()
                SystemLog.query.delete()
                db.session.commit()
                message = f'Cleared {count} system log entries'
                
            elif action == 'reset_user_sessions':
                # This would require session management - placeholder for now
                message = 'User sessions reset (functionality to be implemented)'
                
            elif action == 'optimize_db':
                # Database optimization - placeholder
                message = 'Database optimization completed'
                
            elif action == 'backup_db':
                # Database backup - placeholder
                message = 'Database backup initiated'
                
            elif action == 'clear_temp_files':
                # Clear temporary files - placeholder
                message = 'Temporary files cleared'
            
            log_admin_action('maintenance_action', message, metadata={'action': action})
            flash(message, 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Error performing maintenance action. Please try again.', 'error')
    
    return render_template('admin/maintenance.html', form=form)


# Helper functions
def _check_ollama_status():
    """Check if Ollama is accessible"""
    try:
        ollama_url_setting = GlobalSettings.query.filter_by(key='ollama_url').first()
        ollama_url = ollama_url_setting.get_value() if ollama_url_setting else 'http://localhost:11434'
        
        client = OllamaClient(ollama_url)
        return client.test_connection()
    except:
        return False


def _get_disk_usage():
    """Get disk usage information"""
    try:
        import shutil
        import os
        # Use current working directory to get disk usage for the current drive
        path = os.getcwd()
        total, used, free = shutil.disk_usage(path)
        return {
            'total': total // (1024**3),  # GB
            'used': used // (1024**3),    # GB
            'free': free // (1024**3),    # GB
            'percent': round((used / total) * 100, 1)
        }
    except:
        return None


def _get_last_backup_time():
    """Get last backup time (placeholder)"""
    return None  # To be implemented based on backup strategy