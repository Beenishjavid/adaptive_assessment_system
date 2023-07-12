"""
Groups Models - Enhanced group management system
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string


class Group(models.Model):
    """Enhanced Group model supporting multiple group types and functionality"""
    GROUP_TYPE_CHOICES = [
        ('course', 'Faculty Course Group'),  # Teacher creates for course, students join
        ('study', 'Student Study Group'),    # Students create collaborative groups
        ('public', 'Public Group'),          # Anyone can join public groups
        ('self', 'Self Assessment'),         # Individual student practice
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    
    # Course-specific fields
    course_code = models.CharField(max_length=50, blank=True, null=True, help_text="For course groups")
    subject = models.CharField(max_length=100, blank=True, null=True)
    
    # Group settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    max_members = models.IntegerField(default=50, null=True, blank=True)
    join_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'groups_group'

    def __str__(self):
        return f"{self.name} ({self.get_group_type_display()})"

    def generate_join_code(self):
        """Generate a unique join code for the group"""
        if not self.join_code:
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not Group.objects.filter(join_code=code).exists():
                    self.join_code = code
                    self.save()
                    break
        return self.join_code

    def can_user_join(self, user):
        """Check if a user can join this group"""
        # Check if already a member
        if self.memberships.filter(user=user, is_active=True).exists():
            return False, "Already a member"
        
        # Check group capacity
        if self.max_members and self.memberships.filter(is_active=True).count() >= self.max_members:
            return False, "Group is full"
        
        # Check group type specific rules
        try:
            user_role = user.profile.role if hasattr(user, 'profile') else 'student'
        except:
            user_role = 'student'  # Default fallback
            
        if self.group_type == 'course' and user_role not in ['instructor', 'student']:
            return False, "Only instructors and students can join course groups"
        
        if self.group_type == 'self' and self.created_by != user:
            return False, "Self assessment groups are private"
        
        return True, "Can join"

    @property
    def member_count(self):
        return self.memberships.filter(is_active=True).count()

    @property
    def quiz_count(self):
        return self.assigned_quizzes.filter(quiz__is_active=True).count()

    @property
    def active_assignments(self):
        return self.assigned_quizzes.filter(
            quiz__is_active=True,
            due_date__gte=timezone.now()
        ).count()


class Membership(models.Model):
    """Enhanced Group membership with role-based access control"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),          # Full group management rights
        ('instructor', 'Instructor'), # Can create/assign quizzes
        ('member', 'Member'),        # Basic participation rights
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    role_in_group = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'groups_membership'
        unique_together = ['group', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.role_in_group} in {self.group.name}"

    def can_manage_group(self):
        """Check if user can manage group settings"""
        return self.role_in_group in ['admin'] or self.group.created_by == self.user

    def can_assign_quizzes(self):
        """Check if user can create/assign quizzes to group"""
        return self.role_in_group in ['admin', 'instructor'] or self.group.created_by == self.user

    def can_moderate(self):
        """Check if user can moderate group activities"""
        return self.role_in_group in ['admin', 'instructor']


class GroupInvitation(models.Model):
    """Group invitation system with expiration and tracking"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_invitations')
    
    # For email-based invitations
    email = models.EmailField(null=True, blank=True)
    invitation_code = models.CharField(max_length=50, unique=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField(null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'groups_groupinvitation'

    def __str__(self):
        return f"Invitation to {self.group.name} for {self.invited_user.username if self.invited_user else self.email}"

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

    def can_be_accepted(self):
        return self.status == 'pending' and not self.is_expired()


class QuizAssignment(models.Model):
    """Quiz assignment system for groups"""
    quiz = models.ForeignKey('quizzes.Quiz', on_delete=models.CASCADE, related_name='group_assignments')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='assigned_quizzes')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_assignments')
    
    # Assignment settings
    due_date = models.DateTimeField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=True)
    max_attempts_override = models.IntegerField(null=True, blank=True)
    instructions = models.TextField(blank=True, null=True)
    
    assigned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'groups_quizassignment'
        unique_together = ['quiz', 'group']

    def __str__(self):
        return f"{self.quiz.title} assigned to {self.group.name}"

    @property
    def is_overdue(self):
        return self.due_date and timezone.now() > self.due_date

    def completion_stats(self):
        """Get completion statistics for this assignment"""
        total_members = self.group.memberships.filter(is_active=True).count()
        completed_attempts = self.quiz.attempts.filter(
            user__in=self.group.memberships.filter(is_active=True).values('user'),
            status='completed'
        ).values('user').distinct().count()
        
        return {
            'total_members': total_members,
            'completed': completed_attempts,
            'pending': total_members - completed_attempts,
            'completion_rate': (completed_attempts / total_members * 100) if total_members > 0 else 0
        }
