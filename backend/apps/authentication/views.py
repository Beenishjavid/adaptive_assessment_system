"""
Authentication Views - API endpoints for user management
"""
from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import UserProfile, PasswordResetToken, PasswordResetOTP
from apps.organizations.models import Organization
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    UserListSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    OrganizationSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordWithOTPSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view with user profile information"""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                if hasattr(user, 'profile'):
                    response.data['user'] = UserProfileSerializer(user.profile).data
            except User.DoesNotExist:
                pass
                
        return response


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint with email confirmation"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = serializer.save()
            
            # Send confirmation email
            self.send_confirmation_email(user, serializer.validated_data)
            
            return Response(
                {
                    'message': 'User registered successfully! A confirmation email has been sent.',
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # If user creation fails, return detailed error
            return Response(
                {
                    'error': 'Registration failed',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def send_confirmation_email(self, user, validated_data):
        """Send confirmation email with user credentials"""
        try:
            # Get the plain password from validated data
            password = validated_data.get('password', 'Not available')
            organization = validated_data.get('organization', 'Not specified')
            role = validated_data.get('role', 'student')
            
            # Email content
            subject = 'Welcome to Smart Quiz System - Registration Successful'
            
            message = f"""
Dear {user.get_full_name() or user.username},

Welcome to the Smart Quiz System! Your account has been successfully created.

Here are your account details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 Email: {user.email}
👤 Username: {user.username}
🔑 Password: {password}
🏢 Organization: {organization}
👥 Role: {role.title()}
📅 Registration Date: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT SECURITY NOTES:
• Please change your password after your first login
• Keep your credentials secure and do not share them
• Your account may require approval by an administrator

You can now log in to the Smart Quiz System using your username and password.

If you have any questions or need assistance, please contact our support team.

Best regards,
Smart Quiz System Team
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated message. Please do not reply to this email.
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,  # Don't break registration if email fails
            )
            
        except Exception as e:
            # Log the error but don't break registration
            print(f"Failed to send confirmation email: {e}")


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view for authenticated users"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def update(self, request, *args, **kwargs):
        serializer = UserUpdateSerializer(
            self.get_object(), 
            data=request.data, 
            partial=kwargs.pop('partial', False)
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return updated profile data
        profile_serializer = UserProfileSerializer(self.get_object())
        return Response(profile_serializer.data)


class PasswordChangeView(generics.GenericAPIView):
    """Password change endpoint"""
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )


class UserListView(generics.ListAPIView):
    """User list view for admins"""
    queryset = UserProfile.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'status', 'organization']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['created_at', 'user__date_joined', 'user__last_login']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Only admins can see all users
        if self.request.user.profile.is_admin:
            return UserProfile.objects.select_related('user').all()
        # Instructors can see students in their organization
        elif self.request.user.profile.is_instructor:
            return UserProfile.objects.select_related('user').filter(
                organization=self.request.user.profile.organization,
                role='student'
            )
        # Students can only see themselves
        else:
            return UserProfile.objects.filter(user=self.request.user)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """User detail view for admins to manage users"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def get_queryset(self):
        # Only admins can manage other users
        if self.request.user.profile.is_admin:
            return UserProfile.objects.select_related('user').all()
        # Users can only access their own profile
        else:
            return UserProfile.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_user(request, user_id):
    """Approve a pending user (admin only)"""
    if not request.user.profile.is_admin:
        return Response(
            {'error': 'Only administrators can approve users'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        profile = UserProfile.objects.get(id=user_id)
        if profile.status != 'pending':
            return Response(
                {'error': 'User is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile.approve(request.user)
        return Response(
            {'message': 'User approved successfully'},
            status=status.HTTP_200_OK
        )
    
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def suspend_user(request, user_id):
    """Suspend a user (admin only)"""
    if not request.user.profile.is_admin:
        return Response(
            {'error': 'Only administrators can suspend users'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        profile = UserProfile.objects.get(id=user_id)
        profile.suspend()
        return Response(
            {'message': 'User suspended successfully'},
            status=status.HTTP_200_OK
        )
    
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Get user statistics (admin only)"""
    if not request.user.profile.is_admin:
        return Response(
            {'error': 'Only administrators can view user statistics'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    stats = {
        'total_users': UserProfile.objects.count(),
        'active_users': UserProfile.objects.filter(status='active').count(),
        'pending_users': UserProfile.objects.filter(status='pending').count(),
        'suspended_users': UserProfile.objects.filter(status='suspended').count(),
        'students': UserProfile.objects.filter(role='student').count(),
        'instructors': UserProfile.objects.filter(role='instructor').count(),
        'admins': UserProfile.objects.filter(role='admin').count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)


class ForgotPasswordView(generics.GenericAPIView):
    """Forgot password endpoint"""
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email, is_active=True).first()
        
        # Generate reset token
        reset_token = PasswordResetToken.generate_token(user)
        
        # Send email
        try:
            reset_url = f"{request.scheme}://{request.get_host()}/reset-password?token={reset_token.token}"
            
            send_mail(
                subject='Password Reset - Smart Quiz System',
                message=f'''
Hello {user.get_full_name() or user.username},

You have requested to reset your password. Please click the link below to reset your password:

{reset_url}

This link will expire in 24 hours.

If you did not request this, please ignore this email.

Best regards,
Smart Quiz System Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't expose it to the user
            return Response(
                {'message': 'Password reset email could not be sent. Please contact support.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(
            {'message': 'Password reset email has been sent.'},
            status=status.HTTP_200_OK
        )


class VerifyResetTokenView(generics.GenericAPIView):
    """Verify reset token endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if reset_token.is_valid():
                return Response(
                    {'valid': True, 'email': reset_token.user.email},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'valid': False, 'error': 'Token is expired or already used'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'valid': False, 'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResetPasswordView(generics.GenericAPIView):
    """Reset password endpoint"""
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if not reset_token.is_valid():
                return Response(
                    {'error': 'Token is expired or already used'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Reset password
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.used = True
            reset_token.save()
            
            return Response(
                {'message': 'Password has been reset successfully'},
                status=status.HTTP_200_OK
            )
        
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class OrganizationListView(generics.ListAPIView):
    """Organization list for registration"""
    queryset = Organization.objects.filter(is_active=True)
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.AllowAny]


# OTP-based Password Reset Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_password_reset_otp(request):
    """Send OTP for password reset"""
    serializer = SendOTPSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.filter(email=email, is_active=True).first()
            if not user:
                return Response(
                    {'error': 'No active user found with this email address'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate OTP
            otp_instance = PasswordResetOTP.generate_otp(user, email)
            
            # Send OTP email
            try:
                send_mail(
                    subject='Password Reset - OTP Verification',
                    message=f'''
Dear {user.first_name or user.username},

You have requested to reset your password. Please use the following One-Time Password (OTP) to proceed:

OTP: {otp_instance.otp_code}

This OTP is valid for 10 minutes and can be used only once.

If you did not request this password reset, please ignore this email.

Best regards,
Your Security Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                return Response(
                    {
                        'message': 'OTP sent successfully to your email address',
                        'email': email,
                        'expires_in_minutes': 10
                    },
                    status=status.HTTP_200_OK
                )
                
            except Exception as e:
                return Response(
                    {'error': 'Failed to send OTP email'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': 'Failed to process request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_password_reset_otp(request):
    """Verify OTP for password reset"""
    serializer = VerifyOTPSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']
        
        try:
            user = User.objects.filter(email=email, is_active=True).first()
            if not user:
                return Response(
                    {'error': 'No active user found with this email address'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get latest unused OTP for this user
            otp_instance = PasswordResetOTP.objects.filter(
                user=user,
                email=email,
                used=False
            ).order_by('-created_at').first()
            
            if not otp_instance:
                return Response(
                    {'error': 'No valid OTP found. Please request a new OTP'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify OTP
            is_valid, message = otp_instance.verify_otp(otp_code)
            
            if is_valid:
                return Response(
                    {
                        'message': 'OTP verified successfully',
                        'verified': True,
                        'email': email
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': message, 'verified': False},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': 'Failed to verify OTP'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password_with_otp(request):
    """Reset password after OTP verification"""
    serializer = ResetPasswordWithOTPSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.filter(email=email, is_active=True).first()
            if not user:
                return Response(
                    {'error': 'No active user found with this email address'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get latest verified OTP for this user
            otp_instance = PasswordResetOTP.objects.filter(
                user=user,
                email=email,
                otp_code=otp_code,
                verified=True,
                used=False
            ).order_by('-created_at').first()
            
            if not otp_instance:
                return Response(
                    {'error': 'Invalid or expired OTP. Please verify OTP again'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not otp_instance.is_valid():
                return Response(
                    {'error': 'OTP has expired or been used. Please request a new OTP'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Reset password
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as used
            otp_instance.mark_used()
            
            return Response(
                {
                    'message': 'Password has been reset successfully',
                    'email': email
                },
                status=status.HTTP_200_OK
            )
                
        except Exception as e:
            return Response(
                {'error': 'Failed to reset password'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
