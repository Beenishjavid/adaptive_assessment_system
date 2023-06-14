from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator
import random
import string

class Group(models.Model):
    """Enhanced group management system supporting multiple group types"""
    
    GROUP_TYPES = [
        ('course', 'Course Group'),
        ('study', 'Study Group'), 
        ('public', 'Public Group'),
        ('self', 'Self Assessment'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    
    # Course-specific fields
    course_code = models.CharField(max_length=50, blank=True, null=True, help_text="For course groups")
    subject = models.CharField(max_length=100, blank=True, null=True)
    
    # Group settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    max_members = models.IntegerField(default=50, null=True, blank=True)
    
    # Join code for easy group joining
    join_code = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True,
        validators=[MinLengthValidator(4), MaxLengthValidator(20)],
        help_text="Unique code for joining the group"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_group_type_display()})"
    
    def save(self, *args, **kwargs):
        # Generate join code if not provided
        if not self.join_code:
            self.join_code = self.generate_join_code()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_join_code(length=6):
        """Generate a unique join code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not Group.objects.filter(join_code=code).exists():
                return code
    
    def member_count(self):
        """Get current number of active members"""
        return self.memberships.filter(is_active=True).count()
    
    def is_full(self):
        """Check if group has reached maximum capacity"""
        if self.max_members is None:
            return False
        return self.member_count() >= self.max_members
    
    def can_user_join(self, user):
        """Check if user can join this group"""
        if not self.is_active:
            return False, "Group is not active"
        
        if self.is_full():
            return False, "Group is full"
        
        # Check if user is already a member
        if self.memberships.filter(user=user, is_active=True).exists():
            return False, "User is already a member"
        
        # Additional checks based on group type
        if self.group_type == 'course':
            # Course groups might have additional restrictions
            user_profile = getattr(user, 'userprofile', None)
            if user_profile and user_profile.role == 'student':
                return True, "Can join"
            elif user_profile and user_profile.role in ['instructor', 'admin']:
                return True, "Can join"
            else:
                return False, "Invalid user role for course group"
        
        return True, "Can join"
    
    def add_member(self, user, role='member', added_by=None):
        """Add a user to the group"""
        can_join, message = self.can_user_join(user)
        if not can_join:
            raise ValueError(message)
        
        membership, created = Membership.objects.get_or_create(
            group=self,
            user=user,
            defaults={
                'role_in_group': role,
                'is_active': True
            }
        )
        
        if not created and not membership.is_active:
            membership.is_active = True
            membership.role_in_group = role
            membership.joined_at = timezone.now()
            membership.save()
        
        return membership
    
    def get_admins(self):
        """Get all admin members of the group"""
        return User.objects.filter(
            group_memberships__group=self,
            group_memberships__role_in_group='admin',
            group_memberships__is_active=True
        )
    
    def get_active_members(self):
        """Get all active members of the group"""
        return User.objects.filter(
            group_memberships__group=self,
            group_memberships__is_active=True
        )
    
    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"
        ordering = ['-created_at']

class Membership(models.Model):
    """Group membership with role-based access"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    role_in_group = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} in {self.group.name} ({self.role_in_group})"
    
    def can_manage_group(self):
        """Check if user can manage the group"""
        return self.role_in_group in ['admin', 'moderator'] and self.is_active
    
    def can_invite_members(self):
        """Check if user can invite new members"""
        return self.role_in_group in ['admin', 'moderator'] and self.is_active
    
    def can_create_quizzes(self):
        """Check if user can create quizzes in this group"""
        return self.role_in_group in ['admin', 'moderator'] and self.is_active
    
    class Meta:
        unique_together = ('group', 'user')
        verbose_name = "Group Membership"
        verbose_name_plural = "Group Memberships"
        ordering = ['-joined_at']

class Invitation(models.Model):
    """Group invitation system with expiration"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    invited_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_invitations',
        null=True, 
        blank=True,
        help_text="Specific user invited (null for open invitations)"
    )
    
    invitation_code = models.CharField(max_length=50, unique=True)
    email = models.EmailField(null=True, blank=True, help_text="For email-based invitations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    expires_at = models.DateTimeField(null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        target = self.invited_user.username if self.invited_user else self.email or "Open invitation"
        return f"Invitation to {self.group.name} for {target}"
    
    def save(self, *args, **kwargs):
        # Generate invitation code if not provided
        if not self.invitation_code:
            self.invitation_code = self.generate_invitation_code()
        
        # Set default expiration (7 days from creation)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_invitation_code():
        """Generate a unique invitation code"""
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            if not Invitation.objects.filter(invitation_code=code).exists():
                return code
    
    def is_valid(self):
        """Check if invitation is still valid"""
        if self.status != 'pending':
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            self.status = 'expired'
            self.save()
            return False
        
        return True
    
    def accept(self, user):
        """Accept the invitation"""
        if not self.is_valid():
            raise ValueError("Invitation is not valid")
        
        if self.invited_user and self.invited_user != user:
            raise ValueError("This invitation is not for you")
        
        # Add user to group
        membership = self.group.add_member(user)
        
        # Update invitation status
        self.status = 'accepted'
        self.used_at = timezone.now()
        self.save()
        
        return membership
    
    def decline(self):
        """Decline the invitation"""
        if self.status == 'pending':
            self.status = 'declined'
            self.save()
    
    class Meta:
        verbose_name = "Group Invitation"
        verbose_name_plural = "Group Invitations"
        ordering = ['-created_at']
