"""
Reminder Scheduler Service for NutriCoach
Manages automatic notification reminders using APScheduler
"""

from datetime import datetime, time, timedelta
from typing import Dict, List
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from models import User, Profile, FoodLog
from services.notification_service import ReminderService
from extensions import db

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Service for scheduling automatic reminder notifications"""
    
    def __init__(self, scheduler=None):
        self.scheduler = scheduler
        self.reminder_jobs = {}
    
    def start(self):
        """Start the reminder scheduler"""
        if not self.scheduler:
            logger.warning("No scheduler provided to ReminderScheduler")
            return
        
        try:
            # Schedule daily reminder checks
            self.scheduler.add_job(
                func=self._check_meal_reminders,
                trigger=IntervalTrigger(hours=1),
                id='meal_reminder_check',
                name='Check Meal Reminders',
                replace_existing=True
            )
            
            # Schedule weekly reminders
            self.scheduler.add_job(
                func=self._check_weekly_reminders,
                trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
                id='weekly_reminder_check',
                name='Check Weekly Reminders',
                replace_existing=True
            )
            
            # Cleanup notifications daily
            self.scheduler.add_job(
                func=self._cleanup_old_notifications,
                trigger=CronTrigger(hour=2, minute=0),
                id='notification_cleanup',
                name='Cleanup Old Notifications',
                replace_existing=True
            )
            
            logger.info("Reminder scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start reminder scheduler: {e}")
    
    def _check_meal_reminders(self):
        """Check and send meal reminders based on time of day"""
        try:
            current_hour = datetime.now().hour
            
            # Define meal times (can be made configurable per user later)
            meal_times = {
                'breakfast': (7, 9),   # 7 AM - 9 AM
                'lunch': (12, 14),     # 12 PM - 2 PM
                'dinner': (18, 20),    # 6 PM - 8 PM
            }
            
            # Check which meal time we're in
            current_meal = None
            for meal, (start_hour, end_hour) in meal_times.items():
                if start_hour <= current_hour < end_hour:
                    current_meal = meal
                    break
            
            if not current_meal:
                return
            
            # Get active users
            users = User.query.filter_by(is_active=True).all()
            
            for user in users:
                try:
                    # Check if user has already logged this meal today
                    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                    today_end = today_start + timedelta(days=1)
                    
                    existing_log = FoodLog.query.filter(
                        FoodLog.user_id == user.id,
                        FoodLog.meal == current_meal,
                        FoodLog.logged_at >= today_start,
                        FoodLog.logged_at < today_end
                    ).first()
                    
                    if not existing_log:
                        # Send reminder
                        ReminderService.create_meal_reminder(user.id, current_meal)
                        logger.info(f"Sent {current_meal} reminder to user {user.id}")
                
                except Exception as e:
                    logger.error(f"Failed to process meal reminder for user {user.id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in meal reminder check: {e}")
    
    def _check_weekly_reminders(self):
        """Send weekly reminders (weigh-ins, progress checks, etc.)"""
        try:
            users = User.query.filter_by(is_active=True).all()
            
            for user in users:
                try:
                    # Send weigh-in reminder
                    ReminderService.create_weigh_in_reminder(user.id)
                    logger.info(f"Sent weekly weigh-in reminder to user {user.id}")
                    
                except Exception as e:
                    logger.error(f"Failed to send weekly reminder to user {user.id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in weekly reminder check: {e}")
    
    def _cleanup_old_notifications(self):
        """Clean up expired and old notifications"""
        try:
            from services.notification_service import NotificationService
            
            # Clean up expired notifications
            expired_count = NotificationService.cleanup_expired_notifications()
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired notifications")
            
        except Exception as e:
            logger.error(f"Error in notification cleanup: {e}")
    
    def schedule_custom_reminder(self, user_id: int, reminder_type: str, schedule_time: time):
        """Schedule a custom reminder for a specific user"""
        try:
            job_id = f"custom_reminder_{user_id}_{reminder_type}"
            
            if reminder_type == 'water':
                job_func = lambda: ReminderService.create_water_reminder(user_id)
            elif reminder_type == 'meal':
                job_func = lambda: ReminderService.create_meal_reminder(user_id, 'snack')
            else:
                logger.warning(f"Unknown reminder type: {reminder_type}")
                return False
            
            self.scheduler.add_job(
                func=job_func,
                trigger=CronTrigger(
                    hour=schedule_time.hour,
                    minute=schedule_time.minute
                ),
                id=job_id,
                name=f"Custom {reminder_type} reminder for user {user_id}",
                replace_existing=True
            )
            
            self.reminder_jobs[job_id] = {
                'user_id': user_id,
                'type': reminder_type,
                'time': schedule_time
            }
            
            logger.info(f"Scheduled custom {reminder_type} reminder for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule custom reminder: {e}")
            return False
    
    def cancel_custom_reminder(self, user_id: int, reminder_type: str):
        """Cancel a custom reminder for a specific user"""
        try:
            job_id = f"custom_reminder_{user_id}_{reminder_type}"
            
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                
            if job_id in self.reminder_jobs:
                del self.reminder_jobs[job_id]
                
            logger.info(f"Cancelled custom {reminder_type} reminder for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel custom reminder: {e}")
            return False
    
    def get_user_reminders(self, user_id: int) -> List[Dict]:
        """Get all scheduled reminders for a user"""
        user_reminders = []
        
        for job_id, job_info in self.reminder_jobs.items():
            if job_info['user_id'] == user_id:
                user_reminders.append({
                    'id': job_id,
                    'type': job_info['type'],
                    'time': job_info['time'].strftime('%H:%M'),
                    'active': self.scheduler.get_job(job_id) is not None
                })
        
        return user_reminders
    
    def send_immediate_reminder(self, user_id: int, reminder_type: str, message: str = None):
        """Send an immediate reminder notification"""
        try:
            if reminder_type == 'water':
                ReminderService.create_water_reminder(user_id)
            elif reminder_type == 'weigh_in':
                ReminderService.create_weigh_in_reminder(user_id)
            elif reminder_type.startswith('meal_'):
                meal_type = reminder_type.replace('meal_', '')
                ReminderService.create_meal_reminder(user_id, meal_type)
            else:
                logger.warning(f"Unknown immediate reminder type: {reminder_type}")
                return False
            
            logger.info(f"Sent immediate {reminder_type} reminder to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send immediate reminder: {e}")
            return False


# Global scheduler instance
reminder_scheduler = None


def init_reminder_scheduler(app_scheduler):
    """Initialize the global reminder scheduler"""
    global reminder_scheduler
    
    if reminder_scheduler is None:
        reminder_scheduler = ReminderScheduler(app_scheduler)
        reminder_scheduler.start()
        logger.info("Global reminder scheduler initialized")
    
    return reminder_scheduler


def get_reminder_scheduler():
    """Get the global reminder scheduler instance"""
    return reminder_scheduler


def schedule_user_goal_reminders(user_id: int, profile_data: dict):
    """Schedule reminders based on user goals and preferences"""
    global reminder_scheduler
    
    if not reminder_scheduler:
        logger.warning("Reminder scheduler not initialized")
        return
    
    try:
        # Example: Schedule water reminders every 2 hours for active users
        if profile_data.get('activity_level') in ['active', 'very_active']:
            # This would need to be implemented based on user preferences
            pass
        
        # Example: Schedule meal prep reminders on Sundays
        if profile_data.get('meal_planning', False):
            # This would schedule weekly meal prep reminders
            pass
        
        logger.info(f"Configured goal-based reminders for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to schedule goal reminders for user {user_id}: {e}")


def create_default_notification_templates():
    """Create default notification templates in the database"""
    from models import NotificationTemplate, User
    
    try:
        # Get first admin user to own these templates
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            logger.warning("No admin user found to create default templates")
            return
        
        templates = [
            {
                'name': 'meal_reminder_breakfast',
                'title_template': 'Good Morning, {user_name}! 🌅',
                'message_template': 'Time to fuel your day with a healthy breakfast! Log your morning meal to stay on track with your nutrition goals.',
                'notification_type': 'reminder',
                'category': 'meal_reminder',
                'priority': 'normal'
            },
            {
                'name': 'meal_reminder_lunch',
                'title_template': 'Lunch Time, {user_name}! 🍽️',
                'message_template': 'Take a break and nourish your body with a balanced lunch. Don\'t forget to log your meal!',
                'notification_type': 'reminder',
                'category': 'meal_reminder',
                'priority': 'normal'
            },
            {
                'name': 'meal_reminder_dinner',
                'title_template': 'Dinner Ready, {user_name}? 🌆',
                'message_template': 'End your day with a nutritious dinner. Remember to log your evening meal for complete tracking.',
                'notification_type': 'reminder',
                'category': 'meal_reminder',
                'priority': 'normal'
            },
            {
                'name': 'goal_achievement',
                'title_template': 'Congratulations {user_name}! 🎉',
                'message_template': 'You\'ve achieved your goal! Keep up the excellent work on your nutrition journey.',
                'notification_type': 'action',
                'category': 'goal_achieved',
                'priority': 'high'
            },
            {
                'name': 'weekly_progress',
                'title_template': 'Weekly Check-in Time! 📊',
                'message_template': 'Hi {user_name}, it\'s time for your weekly progress check. Review your achievements and plan for the week ahead!',
                'notification_type': 'reminder',
                'category': 'weigh_in_reminder',
                'priority': 'normal'
            }
        ]
        
        created_count = 0
        for template_data in templates:
            existing = NotificationTemplate.query.filter_by(name=template_data['name']).first()
            if not existing:
                template = NotificationTemplate(
                    created_by=admin_user.id,
                    is_system_template=True,
                    is_active=True,
                    **template_data
                )
                db.session.add(template)
                created_count += 1
        
        if created_count > 0:
            db.session.commit()
            logger.info(f"Created {created_count} default notification templates")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create default notification templates: {e}")