from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    organization = models.CharField(max_length=100, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_users')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()}) - {self.get_status_display()}"
    
    def is_pending_approval(self):
        return self.status == 'pending'
    
    def is_active(self):
        return self.status == 'active'
    
    def can_access_system(self):
        return self.status == 'active'
    
    def assign_to_group(self):
        """Assign user to appropriate Django group based on role"""
        # Remove from all quiz-related groups first
        quiz_groups = Group.objects.filter(name__in=['Quiz_Admins', 'Quiz_Instructors', 'Quiz_Students'])
        self.user.groups.remove(*quiz_groups)
        
        # Assign to appropriate group
        if self.role == 'admin':
            group, created = Group.objects.get_or_create(name='Quiz_Admins')
            self.user.groups.add(group)
            self.user.is_staff = True
            self.user.is_superuser = True
        elif self.role == 'instructor':
            group, created = Group.objects.get_or_create(name='Quiz_Instructors')
            self.user.groups.add(group)
            self.user.is_staff = True
            self.user.is_superuser = False
        else:  # student
            group, created = Group.objects.get_or_create(name='Quiz_Students')
            self.user.groups.add(group)
            self.user.is_staff = False
            self.user.is_superuser = False
        
        self.user.save()
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
        # Set initial status based on role
        if instance.is_superuser:
            profile.role = 'admin'
            profile.status = 'active'
        elif instance.is_staff:
            profile.role = 'instructor'
            profile.status = 'pending'  # Instructors need approval
        else:
            profile.role = 'student'
            profile.status = 'active'  # Students are auto-approved
        profile.save()
        profile.assign_to_group()

@receiver(post_save, sender=UserProfile)
def update_user_groups(sender, instance, **kwargs):
    """Update user groups when profile is saved"""
    instance.assign_to_group()
