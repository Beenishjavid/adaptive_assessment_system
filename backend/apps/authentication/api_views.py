"""
Authentication API Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.models import UserProfile


@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """Login API with JWT tokens"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # Get or create user profile
                try:
                    user_profile = user.profile
                    role = user_profile.role
                    full_name = user_profile.full_name
                    organization = user_profile.organization
                except (UserProfile.DoesNotExist, AttributeError):
                    # Create a default profile if none exists
                    if user.is_superuser:
                        role = 'admin'
                    elif user.is_staff:
                        role = 'instructor'
                    else:
                        role = 'student'
                    
                    full_name = f"{user.first_name} {user.last_name}".strip() or user.username
                    organization = None
                    
                    user_profile = UserProfile.objects.create(
                        user=user, 
                        role=role
                    )
                
                return Response({
                    'access': str(access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': full_name,
                        'role': role,
                        'organization': organization,
                        'is_active': user.is_active
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'User account is disabled'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                {'error': 'Invalid username or password'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        return Response(
            {'error': f'Login error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def logout_api(request):
    """Logout API"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_api(request):
    """Refresh JWT token"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token
        
        return Response({
            'access': str(access_token)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Invalid refresh token'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
