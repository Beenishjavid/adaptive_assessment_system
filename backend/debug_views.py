"""
Debug views for testing user profile relationships
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from apps.authentication.models import UserProfile


@api_view(['GET'])
@permission_classes([AllowAny])
def debug_users(request):
    """Debug endpoint to check user-profile relationships"""
    results = []
    
    for user in User.objects.all():
        try:
            profile = user.profile
            results.append({
                'username': user.username,
                'has_profile': True,
                'profile_role': profile.role,
                'profile_status': profile.status,
                'access_method': 'user.profile'
            })
        except UserProfile.DoesNotExist:
            results.append({
                'username': user.username,
                'has_profile': False,
                'error': 'UserProfile.DoesNotExist',
                'access_method': 'user.profile'
            })
        except AttributeError as e:
            results.append({
                'username': user.username,
                'has_profile': False,
                'error': f'AttributeError: {str(e)}',
                'access_method': 'user.profile'
            })
    
    return Response({
        'total_users': User.objects.count(),
        'total_profiles': UserProfile.objects.count(),
        'user_details': results
    })
