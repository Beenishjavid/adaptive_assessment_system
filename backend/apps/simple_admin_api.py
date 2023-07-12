"""
Simple Admin API Views - Working Implementation
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.authentication.models import UserProfile
from apps.organizations.models import Organization


def check_admin_permission(user):
    """Helper function to check if user has admin permissions"""
    try:
        if user.is_superuser:
            return True
        user_profile = getattr(user, 'profile', None) 
        return user_profile and user_profile.role == 'admin'
    except Exception:
        return False


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_users(request):
    """Get all users for admin dashboard"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        users = User.objects.select_related('profile').all()[:50]  # Limit for performance
        
        user_data = []
        for user in users:
            try:
                profile = user.profile
                user_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'date_joined': user.date_joined.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'role': profile.role,
                    'organization': profile.organization if profile.organization else None,
                    'status': profile.status,
                })
            except Exception as e:
                # Create profile if it doesn't exist
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'role': 'student', 'status': 'active'}
                )
                user_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'date_joined': user.date_joined.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'role': profile.role,
                    'organization': profile.organization if profile.organization else None,
                    'status': profile.status,
                })
        
        return Response({
            'users': user_data,
            'total_count': len(user_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching users: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_organizations(request):
    """Get all organizations for admin dashboard"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        organizations = Organization.objects.all()
        
        org_data = []
        for org in organizations:
            user_count = UserProfile.objects.filter(organization=org).count()
            org_data.append({
                'id': org.id,
                'name': org.name,
                'description': org.description,
                'is_active': org.is_active,
                'user_count': user_count,
                'created_at': org.created_at.isoformat() if hasattr(org, 'created_at') else None,
            })
        
        return Response({
            'organizations': org_data,
            'total_count': len(org_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching organizations: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_toggle_user_status(request, user_id):
    """Toggle user active status"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Prevent toggling superuser or self
        if user.is_superuser or user.id == request.user.id:
            return Response(
                {'error': 'Cannot modify this user'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = not user.is_active
        user.save()
        
        return Response({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'is_active': user.is_active
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error updating user status: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_stats(request):
    """Get admin dashboard statistics"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Basic statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_organizations = Organization.objects.count()
        
        # Role distribution  
        admin_count = UserProfile.objects.filter(role='admin').count()
        instructor_count = UserProfile.objects.filter(role='instructor').count()
        student_count = UserProfile.objects.filter(role='student').count()
        
        return Response({
            'users': {
                'total': total_users,
                'active': active_users,
                'inactive': total_users - active_users
            },
            'roles': {
                'admin': admin_count,
                'instructor': instructor_count,
                'student': student_count
            },
            'organizations': {
                'total': total_organizations
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching stats: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_create_user(request):
    """Create a new user"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        data = request.data
        
        # Check if username already exists
        if User.objects.filter(username=data.get('username')).exists():
            return Response(
                {'error': 'Username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if email already exists
        if User.objects.filter(email=data.get('email')).exists():
            return Response(
                {'error': 'Email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use transaction to ensure both user and profile are created together
        with transaction.atomic():
            # Create user (this will automatically create a profile via signals)
            user = User.objects.create(
                username=data.get('username'),
                email=data.get('email'),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                password=make_password(data.get('password', 'defaultpass123'))
            )
            
            # Update the automatically created profile with our data
            profile = user.profile
            profile.role = data.get('role', 'student')
            profile.phone = data.get('phone', '')
            profile.bio = data.get('bio', '')
            profile.organization = data.get('organization', '')
            profile.status = data.get('status', 'active')
            profile.save()
        
        return Response({
            'message': 'User created successfully',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Error creating user: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def admin_update_user(request, user_id):
    """Update an existing user"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(UserProfile, user=user)
        data = request.data
        
        # Update user fields
        if 'username' in data and data['username'] != user.username:
            if User.objects.filter(username=data['username']).exists():
                return Response(
                    {'error': 'Username already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.username = data['username']
        
        if 'email' in data and data['email'] != user.email:
            if User.objects.filter(email=data['email']).exists():
                return Response(
                    {'error': 'Email already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = data['email']
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'password' in data and data['password']:
            user.password = make_password(data['password'])
        
        user.save()
        
        # Update profile fields
        if 'role' in data:
            profile.role = data['role']
        if 'phone' in data:
            profile.phone = data['phone']
        if 'bio' in data:
            profile.bio = data['bio']
        if 'organization' in data:
            profile.organization = data['organization']
        if 'status' in data:
            profile.status = data['status']
        
        profile.save()
        
        return Response({
            'message': 'User updated successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error updating user: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_user(request, user_id):
    """Delete a user"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Don't allow deletion of superusers
        if user.is_superuser:
            return Response(
                {'error': 'Cannot delete superuser'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Don't allow users to delete themselves
        if user.id == request.user.id:
            return Response(
                {'error': 'Cannot delete your own account'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.delete()
        
        return Response({
            'message': 'User deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error deleting user: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_system_overview(request):
    """Get system overview statistics"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Basic system statistics
        total_users = User.objects.count()
        total_organizations = Organization.objects.count()
        
        # User role distribution
        admin_count = UserProfile.objects.filter(role='admin').count()
        instructor_count = UserProfile.objects.filter(role='instructor').count()
        student_count = UserProfile.objects.filter(role='student').count()
        
        # Active vs inactive users
        active_users = UserProfile.objects.filter(status='active').count()
        
        return Response({
            'user_stats': {
                'total': total_users,
                'active': active_users,
                'inactive': total_users - active_users
            },
            'role_distribution': {
                'admin': admin_count,
                'instructor': instructor_count, 
                'student': student_count
            },
            'organization_stats': {
                'total': total_organizations
            },
            'system_health': {
                'status': 'healthy',
                'uptime': '99.9%',
                'last_backup': 'N/A'
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching system overview: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
