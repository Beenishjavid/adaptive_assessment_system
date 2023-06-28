"""
Authentication Models - User Profile and Organization Management
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
import random
import string


class UserProfile(models.Model):
    """Extended user profile with role and organization information"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, null=True, blank=True)
    bio = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    date_of_birth = models.DateField(null=True, blank=True)
    organization = models.CharField(max_length=100, null=True, blank=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_users'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_instructor(self):
        return self.role == 'instructor'
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    def approve(self, approved_by_user):
        """Approve user profile"""
        self.status = 'active'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()
    
    def suspend(self):
        """Suspend user profile"""
        self.status = 'suspended'
        self.save()
    
    def reject(self):
        """Reject user profile"""
        self.status = 'rejected'
        self.save()


class PasswordResetOTP(models.Model):
    """OTP-based password reset for forgot password functionality"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    
    class Meta:
        db_table = 'auth_password_reset_otp'
        verbose_name = 'Password Reset OTP'
        verbose_name_plural = 'Password Reset OTPs'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # OTP expires in 10 minutes
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return (not self.used and 
                not self.is_expired() and 
                self.attempts < self.max_attempts)
    
    def verify_otp(self, otp_input):
        """Verify the OTP code"""
        self.attempts += 1
        
        if not self.is_valid():
            self.save()
            return False, "OTP has expired or maximum attempts exceeded"
        
        if self.otp_code != otp_input:
            self.save()
            remaining = self.max_attempts - self.attempts
            if remaining > 0:
                return False, f"Invalid OTP. {remaining} attempts remaining"
            else:
                return False, "Invalid OTP. Maximum attempts exceeded"
        
        # OTP is correct
        self.verified = True
        self.save()
        return True, "OTP verified successfully"
    
    def mark_used(self):
        """Mark OTP as used after successful password reset"""
        self.used = True
        self.save()
    
    @classmethod
    def generate_otp(cls, user, email):
        """Generate a new OTP for password reset"""
        # Invalidate any existing unused OTPs for this user
        cls.objects.filter(user=user, used=False).update(used=True)
        
        # Generate 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        return cls.objects.create(
            user=user,
            email=email,
            otp_code=otp_code
        )


class PasswordResetToken(models.Model):
    """Legacy password reset token - keeping for backward compatibility"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'auth_password_reset_tokens'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.used and not self.is_expired()
    
    @classmethod
    def generate_token(cls, user):
        """Generate a new password reset token"""
        # Invalidate any existing tokens
        cls.objects.filter(user=user, used=False).update(used=True)
        
        # Generate new token
        token = get_random_string(64)
        return cls.objects.create(user=user, token=token)
