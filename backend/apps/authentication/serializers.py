"""
Authentication Serializers for API endpoints
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, PasswordResetOTP
from apps.organizations.models import Organization


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with user profile information"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        if hasattr(user, 'profile'):
            token['role'] = user.profile.role
            token['status'] = user.profile.status
            token['organization'] = user.profile.organization
        
        token['full_name'] = user.get_full_name() or user.username
        token['email'] = user.email
        
        return token


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    
    full_name = serializers.ReadOnlyField()
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'bio', 'status', 'date_of_birth', 'organization',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    organization = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password', 
            'password_confirm', 'role', 'phone', 'bio', 'date_of_birth', 
            'organization'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password fields didn't match.")
        
        # Check if email already exists
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        
        return attrs
    
    def create(self, validated_data):
        # Extract profile data
        profile_data = {
            'role': validated_data.pop('role'),
            'phone': validated_data.pop('phone', ''),
            'bio': validated_data.pop('bio', ''),
            'date_of_birth': validated_data.pop('date_of_birth', None),
            'organization': validated_data.pop('organization', ''),
        }
        
        # Remove password_confirm and create user
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        try:
            # Create user
            user = User.objects.create_user(**validated_data)
            user.set_password(password)
            user.save()
            
            # Create profile, but check if one already exists
            profile, created = UserProfile.objects.get_or_create(
                user=user, 
                defaults=profile_data
            )
            
            if not created:
                # Update existing profile
                for key, value in profile_data.items():
                    setattr(profile, key, value)
                profile.save()
            
            return user
            
        except Exception as e:
            # Clean up if user was created but profile failed
            if 'user' in locals():
                user.delete()
            raise e


class UserUpdateSerializer(serializers.ModelSerializer):
    """User update serializer"""
    
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'bio', 
            'date_of_birth', 'organization'
        ]
    
    def update(self, instance, validated_data):
        # Update user fields
        user_data = validated_data.pop('user', {})
        for field, value in user_data.items():
            setattr(instance.user, field, value)
        instance.user.save()
        
        # Update profile fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New password fields didn't match.")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user list display"""
    
    full_name = serializers.ReadOnlyField()
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    last_login = serializers.DateTimeField(source='user.last_login', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'full_name', 'role', 'status', 
            'organization', 'last_login', 'date_joined', 'created_at'
        ]


class ForgotPasswordSerializer(serializers.Serializer):
    """Forgot password serializer"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        try:
            # Use filter().first() to handle multiple users with same email
            user = User.objects.filter(email=value, is_active=True).first()
            if not user:
                raise serializers.ValidationError("No active user found with this email address.")
            return value
        except Exception:
            raise serializers.ValidationError("No active user found with this email address.")


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password serializer"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs


class OrganizationSerializer(serializers.Serializer):
    """Organization serializer for registration"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()


# OTP-based Password Reset Serializers
class SendOTPSerializer(serializers.Serializer):
    """Send OTP for password reset"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        try:
            user = User.objects.filter(email=value, is_active=True).first()
            if not user:
                raise serializers.ValidationError("No active user found with this email address.")
            return value
        except Exception:
            raise serializers.ValidationError("No active user found with this email address.")


class VerifyOTPSerializer(serializers.Serializer):
    """Verify OTP for password reset"""
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)
    
    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be a 6-digit number.")
        return value


class ResetPasswordWithOTPSerializer(serializers.Serializer):
    """Reset password after OTP verification"""
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be a 6-digit number.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs
