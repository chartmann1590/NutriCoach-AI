"""
Notification Service for NutriCoach
Handles creation, management, and delivery of user notifications
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_
from models import Notification, NotificationTemplate, User, FoodLog, Profile
from extensions import db
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing user notifications"""
    
    @staticmethod
    def create_notification(
        user_id: int,
        title: str,
        message: str,
        notification_type: str = 'system',
        category: str = None,
        priority: str = 'normal',
        action_url: str = None,
        action_data: Dict = None,
        expires_at: datetime = None,
        created_by: int = None
    ) -> Notification:
        """Create a new notification for a user"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                category=category,
                priority=priority,
                action_url=action_url,
                expires_at=expires_at,
                created_by=created_by
            )
            
            if action_data:
                notification.set_action_data(action_data)
            
            db.session.add(notification)
            db.session.commit()
            
            logger.info(f"Created notification {notification.id} for user {user_id}")
            return notification
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create notification: {e}")
            raise
    
    @staticmethod
    def create_notification_from_template(
        template_name: str,
        user_id: int,
        template_vars: Dict = None,
        created_by: int = None
    ) -> Optional[Notification]:
        """Create notification from template"""
        try:
            template = NotificationTemplate.query.filter_by(
                name=template_name,
                is_active=True
            ).first()
            
            if not template:
                logger.warning(f"Template '{template_name}' not found or inactive")
                return None
            
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                return None
            
            # Prepare template variables
            vars_dict = template_vars or {}
            
            # Render template
            title = template.render_title(user, **vars_dict)
            message = template.render_message(user, **vars_dict)
            
            return NotificationService.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=template.notification_type,
                category=template.category,
                priority=template.priority,
                created_by=created_by
            )
            
        except Exception as e:
            logger.error(f"Failed to create notification from template: {e}")
            return None
    
    @staticmethod
    def get_user_notifications(
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        include_dismissed: bool = False
    ) -> List[Notification]:
        """Get notifications for a user"""
        try:
            query = Notification.query.filter_by(user_id=user_id)
            
            if unread_only:
                query = query.filter_by(is_read=False)
            
            if not include_dismissed:
                query = query.filter_by(is_dismissed=False)
            
            # Filter out expired notifications
            query = query.filter(
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )
            
            return query.order_by(Notification.created_at.desc())\
                       .limit(limit).offset(offset).all()
            
        except Exception as e:
            logger.error(f"Failed to get notifications for user {user_id}: {e}")
            return []
    
    @staticmethod
    def get_notification_counts(user_id: int) -> Dict[str, int]:
        """Get notification counts for a user"""
        try:
            # Total unread
            unread_count = Notification.query.filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    Notification.is_dismissed == False,
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > datetime.utcnow()
                    )
                )
            ).count()
            
            # Unread by priority
            high_priority_count = Notification.query.filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    Notification.is_dismissed == False,
                    Notification.priority.in_(['high', 'urgent']),
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > datetime.utcnow()
                    )
                )
            ).count()
            
            return {
                'total_unread': unread_count,
                'high_priority_unread': high_priority_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get notification counts for user {user_id}: {e}")
            return {'total_unread': 0, 'high_priority_unread': 0}
    
    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if notification:
                notification.mark_as_read()
                db.session.commit()
                logger.info(f"Marked notification {notification_id} as read")
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to mark notification as read: {e}")
            return False
    
    @staticmethod
    def mark_multiple_as_read(notification_ids: List[int], user_id: int) -> int:
        """Mark multiple notifications as read, returns count of updated notifications"""
        try:
            count = 0
            notifications = Notification.query.filter(
                and_(
                    Notification.id.in_(notification_ids),
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            ).all()
            
            for notification in notifications:
                notification.mark_as_read()
                count += 1
            
            db.session.commit()
            logger.info(f"Marked {count} notifications as read for user {user_id}")
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to mark multiple notifications as read: {e}")
            return 0
    
    @staticmethod
    def dismiss_notification(notification_id: int, user_id: int) -> bool:
        """Dismiss a notification"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if notification:
                notification.dismiss()
                db.session.commit()
                logger.info(f"Dismissed notification {notification_id}")
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to dismiss notification: {e}")
            return False
    
    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        """Mark all notifications as read for a user"""
        try:
            notifications = Notification.query.filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    Notification.is_dismissed == False
                )
            ).all()
            
            count = 0
            for notification in notifications:
                notification.mark_as_read()
                count += 1
            
            db.session.commit()
            logger.info(f"Marked all {count} notifications as read for user {user_id}")
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to mark all notifications as read: {e}")
            return 0
    
    @staticmethod
    def cleanup_expired_notifications() -> int:
        """Remove expired notifications"""
        try:
            expired = Notification.query.filter(
                and_(
                    Notification.expires_at.isnot(None),
                    Notification.expires_at <= datetime.utcnow()
                )
            ).all()
            
            count = len(expired)
            for notification in expired:
                db.session.delete(notification)
            
            db.session.commit()
            logger.info(f"Cleaned up {count} expired notifications")
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to cleanup expired notifications: {e}")
            return 0


class ActionNotificationService:
    """Service for creating action-based notifications"""
    
    @staticmethod
    def notify_food_logged(user_id: int, food_log: FoodLog):
        """Notify user when food is successfully logged"""
        try:
            meal_name = food_log.meal.replace('_', ' ').title()
            
            NotificationService.create_notification(
                user_id=user_id,
                title="Food Logged Successfully! 🍽️",
                message=f"Great job! You've logged {food_log.custom_name} for {meal_name}. "
                       f"Calories: {food_log.calories}",
                notification_type='action',
                category='food_logged',
                priority='low',
                action_url='/dashboard',
                expires_at=datetime.utcnow() + timedelta(hours=6)
            )
            
        except Exception as e:
            logger.error(f"Failed to create food logged notification: {e}")
    
    @staticmethod
    def notify_goal_achieved(user_id: int, goal_type: str, details: str):
        """Notify user when they achieve a goal"""
        try:
            title_map = {
                'daily_calories': "Daily Calorie Goal Achieved! 🎯",
                'weekly_weight': "Weekly Weight Goal Met! 📊",
                'consistency': "Consistency Streak! 🔥"
            }
            
            NotificationService.create_notification(
                user_id=user_id,
                title=title_map.get(goal_type, "Goal Achieved! 🏆"),
                message=f"Congratulations! {details}",
                notification_type='action',
                category='goal_achieved',
                priority='high',
                action_url='/progress',
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            
        except Exception as e:
            logger.error(f"Failed to create goal achieved notification: {e}")
    
    @staticmethod
    def notify_photo_analyzed(user_id: int, photo_id: int, food_count: int):
        """Notify user when photo analysis is complete"""
        try:
            message = f"Your food photo has been analyzed! We detected {food_count} food items. " \
                     f"Review and confirm the results to add them to your log."
            
            NotificationService.create_notification(
                user_id=user_id,
                title="Photo Analysis Complete! 📷",
                message=message,
                notification_type='action',
                category='photo_analyzed',
                priority='normal',
                action_url=f'/photo/{photo_id}',
                action_data={'photo_id': photo_id, 'food_count': food_count},
                expires_at=datetime.utcnow() + timedelta(hours=12)
            )
            
        except Exception as e:
            logger.error(f"Failed to create photo analyzed notification: {e}")


class ReminderService:
    """Service for creating reminder notifications"""
    
    @staticmethod
    def create_meal_reminder(user_id: int, meal_type: str):
        """Create a meal reminder notification"""
        try:
            user = User.query.get(user_id)
            if not user or not user.profile:
                return
            
            meal_name = meal_type.replace('_', ' ').title()
            user_name = user.profile.name
            
            # Check if user has already logged this meal today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            existing_log = FoodLog.query.filter(
                and_(
                    FoodLog.user_id == user_id,
                    FoodLog.meal == meal_type,
                    FoodLog.logged_at >= today_start,
                    FoodLog.logged_at < today_end
                )
            ).first()
            
            if existing_log:
                logger.info(f"User {user_id} already logged {meal_type} today, skipping reminder")
                return
            
            NotificationService.create_notification(
                user_id=user_id,
                title=f"Time for {meal_name}! 🍽️",
                message=f"Hi {user_name}! Don't forget to log your {meal_name.lower()}. "
                       f"Keeping track helps you stay on track with your nutrition goals.",
                notification_type='reminder',
                category='meal_reminder',
                priority='normal',
                action_url='/log-food',
                action_data={'suggested_meal': meal_type},
                expires_at=datetime.utcnow() + timedelta(hours=3)
            )
            
        except Exception as e:
            logger.error(f"Failed to create meal reminder: {e}")
    
    @staticmethod
    def create_water_reminder(user_id: int):
        """Create a water intake reminder"""
        try:
            NotificationService.create_notification(
                user_id=user_id,
                title="Stay Hydrated! 💧",
                message="Remember to drink water throughout the day. "
                       "Proper hydration is essential for your health and nutrition goals.",
                notification_type='reminder',
                category='water_reminder',
                priority='low',
                action_url='/dashboard',
                expires_at=datetime.utcnow() + timedelta(hours=4)
            )
            
        except Exception as e:
            logger.error(f"Failed to create water reminder: {e}")
    
    @staticmethod
    def create_weigh_in_reminder(user_id: int):
        """Create a weigh-in reminder"""
        try:
            NotificationService.create_notification(
                user_id=user_id,
                title="Weekly Check-in Time! ⚖️",
                message="It's time for your weekly weigh-in. "
                       "Tracking your progress helps you stay motivated!",
                notification_type='reminder',
                category='weigh_in_reminder',
                priority='normal',
                action_url='/progress',
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            
        except Exception as e:
            logger.error(f"Failed to create weigh-in reminder: {e}")


class AdminNotificationService:
    """Service for admin-created notifications"""
    
    @staticmethod
    def send_to_user(
        admin_user_id: int,
        target_user_id: int,
        title: str,
        message: str,
        priority: str = 'normal'
    ) -> Optional[Notification]:
        """Send notification from admin to specific user"""
        try:
            return NotificationService.create_notification(
                user_id=target_user_id,
                title=title,
                message=message,
                notification_type='admin',
                category='admin_message',
                priority=priority,
                created_by=admin_user_id
            )
            
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}")
            return None
    
    @staticmethod
    def send_to_all_users(
        admin_user_id: int,
        title: str,
        message: str,
        priority: str = 'normal',
        exclude_user_ids: List[int] = None
    ) -> int:
        """Send notification to all users (broadcast)"""
        try:
            query = User.query.filter_by(is_active=True)
            
            if exclude_user_ids:
                query = query.filter(~User.id.in_(exclude_user_ids))
            
            users = query.all()
            count = 0
            
            for user in users:
                notification = NotificationService.create_notification(
                    user_id=user.id,
                    title=title,
                    message=message,
                    notification_type='admin',
                    category='admin_broadcast',
                    priority=priority,
                    created_by=admin_user_id
                )
                if notification:
                    count += 1
            
            logger.info(f"Admin {admin_user_id} sent broadcast to {count} users")
            return count
            
        except Exception as e:
            logger.error(f"Failed to send broadcast notification: {e}")
            return 0
    
    @staticmethod
    def create_system_announcement(
        admin_user_id: int,
        title: str,
        message: str,
        expires_at: datetime = None
    ) -> int:
        """Create system-wide announcement"""
        try:
            if not expires_at:
                expires_at = datetime.utcnow() + timedelta(days=7)
            
            return AdminNotificationService.send_to_all_users(
                admin_user_id=admin_user_id,
                title=f"📢 System Announcement: {title}",
                message=message,
                priority='high'
            )
            
        except Exception as e:
            logger.error(f"Failed to create system announcement: {e}")
            return 0