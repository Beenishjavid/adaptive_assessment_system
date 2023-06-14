from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    """Notification system for group activities and quiz assignments"""
    
    NOTIFICATION_TYPES = [
        ('quiz_assigned', 'Quiz Assigned'),
        ('group_invitation', 'Group Invitation'),
        ('quiz_completed', 'Quiz Completed'),
        ('group_joined', 'Group Joined'),
        ('announcement', 'Announcement'),
        ('quiz_reminder', 'Quiz Reminder'),
        ('grade_released', 'Grade Released'),
        ('group_updated', 'Group Updated'),
        ('deadline_approaching', 'Deadline Approaching'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sent_notifications'
    )
    
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    related_quiz = models.ForeignKey(
        'quizzes.Quiz', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    related_group = models.ForeignKey(
        'groups.Group', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    
    # Notification status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Additional data (JSON field for flexible data storage)
    extra_data = models.JSONField(null=True, blank=True, help_text="Additional notification data")
    
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.recipient.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def is_recent(self):
        """Check if notification was created within the last 24 hours"""
        return (timezone.now() - self.created_at).days < 1
    
    @property
    def time_since_created(self):
        """Get human-readable time since creation"""
        delta = timezone.now() - self.created_at
        
        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    @classmethod
    def create_quiz_assignment_notification(cls, quiz, group, assigned_by, recipients=None):
        """Create notifications for quiz assignment"""
        if recipients is None:
            # Get all active group members
            recipients = User.objects.filter(
                group_memberships__group=group,
                group_memberships__is_active=True
            ).exclude(id=assigned_by.id)
        
        notifications = []
        for recipient in recipients:
            notification = cls.objects.create(
                recipient=recipient,
                sender=assigned_by,
                notification_type='quiz_assigned',
                title=f"New Quiz Assigned: {quiz.title}",
                message=f"A new quiz '{quiz.title}' has been assigned to your group '{group.name}'.",
                related_quiz=quiz,
                related_group=group,
                extra_data={
                    'quiz_id': quiz.id,
                    'group_id': group.id,
                    'due_date': quiz.end_time.isoformat() if quiz.end_time else None
                }
            )
            notifications.append(notification)
        
        return notifications
    
    @classmethod
    def create_group_invitation_notification(cls, invitation, invited_user):
        """Create notification for group invitation"""
        return cls.objects.create(
            recipient=invited_user,
            sender=invitation.invited_by,
            notification_type='group_invitation',
            title=f"Group Invitation: {invitation.group.name}",
            message=f"You've been invited to join the group '{invitation.group.name}'.",
            related_group=invitation.group,
            extra_data={
                'invitation_id': invitation.id,
                'group_id': invitation.group.id,
                'invitation_code': invitation.invitation_code
            }
        )
    
    @classmethod
    def create_quiz_completion_notification(cls, quiz_attempt, notify_instructors=True):
        """Create notifications for quiz completion"""
        notifications = []
        
        if notify_instructors and quiz_attempt.quiz.group_id:
            # Notify group admins/instructors
            instructors = User.objects.filter(
                group_memberships__group=quiz_attempt.quiz.group_id,
                group_memberships__role_in_group__in=['admin', 'moderator'],
                group_memberships__is_active=True
            )
            
            for instructor in instructors:
                notification = cls.objects.create(
                    recipient=instructor,
                    sender=quiz_attempt.user,
                    notification_type='quiz_completed',
                    title=f"Quiz Completed: {quiz_attempt.quiz.title}",
                    message=f"{quiz_attempt.user.get_full_name() or quiz_attempt.user.username} has completed the quiz '{quiz_attempt.quiz.title}'.",
                    related_quiz=quiz_attempt.quiz,
                    related_group=quiz_attempt.quiz.group if hasattr(quiz_attempt.quiz, 'group') else None,
                    extra_data={
                        'quiz_attempt_id': quiz_attempt.id,
                        'score': quiz_attempt.score,
                        'percentage': quiz_attempt.percentage
                    }
                )
                notifications.append(notification)
        
        return notifications
    
    @classmethod
    def create_group_join_notification(cls, membership):
        """Create notification for new group member"""
        # Notify group admins
        admins = User.objects.filter(
            group_memberships__group=membership.group,
            group_memberships__role_in_group='admin',
            group_memberships__is_active=True
        ).exclude(id=membership.user.id)
        
        notifications = []
        for admin in admins:
            notification = cls.objects.create(
                recipient=admin,
                sender=membership.user,
                notification_type='group_joined',
                title=f"New Member: {membership.group.name}",
                message=f"{membership.user.get_full_name() or membership.user.username} has joined the group '{membership.group.name}'.",
                related_group=membership.group,
                extra_data={
                    'membership_id': membership.id,
                    'user_id': membership.user.id
                }
            )
            notifications.append(notification)
        
        return notifications
    
    @classmethod
    def create_announcement_notification(cls, group, sender, title, message, recipients=None):
        """Create announcement notifications for group members"""
        if recipients is None:
            recipients = User.objects.filter(
                group_memberships__group=group,
                group_memberships__is_active=True
            ).exclude(id=sender.id)
        
        notifications = []
        for recipient in recipients:
            notification = cls.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type='announcement',
                title=title,
                message=message,
                related_group=group,
                extra_data={
                    'group_id': group.id
                }
            )
            notifications.append(notification)
        
        return notifications
    
    @classmethod
    def get_unread_count(cls, user):
        """Get count of unread notifications for user"""
        return cls.objects.filter(recipient=user, is_read=False).count()
    
    @classmethod
    def mark_all_as_read(cls, user):
        """Mark all notifications as read for user"""
        return cls.objects.filter(recipient=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['notification_type']),
        ]
