"""
Organizations Models - Multi-tenant support
"""
from django.db import models
from django.utils import timezone


class Organization(models.Model):
    """Organization model for multi-tenant support"""
    
    SUBSCRIPTION_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=100, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    subscription_type = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_CHOICES, 
        default='basic'
    )
    max_users = models.IntegerField(default=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations_organization'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def user_count(self):
        """Get current user count for this organization"""
        from apps.authentication.models import UserProfile
        # Match by organization name (case-insensitive and partial match)
        return UserProfile.objects.filter(organization__icontains=self.name).count()
    
    @property
    def can_add_users(self):
        """Check if organization can add more users"""
        return self.user_count < self.max_users
    
    def get_subscription_features(self):
        """Get features based on subscription type"""
        features = {
            'basic': {
                'max_users': 100,
                'max_quizzes': 50,
                'storage_gb': 5,
                'email_support': True,
                'advanced_analytics': False,
                'proctoring': False,
            },
            'premium': {
                'max_users': 500,
                'max_quizzes': 200,
                'storage_gb': 25,
                'email_support': True,
                'advanced_analytics': True,
                'proctoring': True,
            },
            'enterprise': {
                'max_users': -1,  # Unlimited
                'max_quizzes': -1,  # Unlimited
                'storage_gb': 100,
                'email_support': True,
                'advanced_analytics': True,
                'proctoring': True,
            }
        }
        return features.get(self.subscription_type, features['basic'])
