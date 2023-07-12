"""
General Admin API Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from apps.authentication.models import UserProfile
from apps.quizzes.models import Quiz
from apps.results.models import QuizAttempt
from apps.organizations.models import Organization
from datetime import datetime, timedelta
from django.db.models import Q


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_activity(request):
    """Get recent system activity across all apps"""
    if request.user.profile.role != 'admin':
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        days = int(request.GET.get('days', 30))
        date_threshold = datetime.now() - timedelta(days=days)
        
        activities = []
        
        # Recent user registrations
        recent_users = User.objects.filter(
            date_joined__gte=date_threshold
        ).select_related('profile')[:10]
        
        for user in recent_users:
            activities.append({
                'user': 'System',
                'action': f'New user registered: {user.get_full_name() or user.username}',
                'timestamp': user.date_joined.isoformat(),
                'icon': '👤',
                'status': 'success',
                'type': 'user_registration'
            })
        
        # Recent quiz creations
        if hasattr(Quiz, 'created_at'):
            recent_quizzes = Quiz.objects.filter(
                created_at__gte=date_threshold
            ).select_related('created_by')[:10]
            
            for quiz in recent_quizzes:
                activities.append({
                    'user': quiz.created_by.get_full_name() or quiz.created_by.username,
                    'action': f'created quiz "{quiz.title}"',
                    'timestamp': quiz.created_at.isoformat(),
                    'icon': '📝',
                    'status': 'success',
                    'type': 'quiz_creation'
                })
        
        # Recent quiz attempts
        recent_attempts = QuizAttempt.objects.filter(
            started_at__gte=date_threshold
        ).select_related('user', 'quiz').order_by('-started_at')[:15]
        
        for attempt in recent_attempts:
            if attempt.status == 'completed':
                action = f'completed quiz "{attempt.quiz.title}"'
                if attempt.score is not None:
                    action += f' (Score: {attempt.score}%)'
                status = 'success' if (attempt.score or 0) >= attempt.quiz.passing_score else 'warning'
            else:
                action = f'started quiz "{attempt.quiz.title}"'
                status = 'success'
            
            activities.append({
                'user': attempt.user.get_full_name() or attempt.user.username,
                'action': action,
                'timestamp': attempt.started_at.isoformat(),
                'icon': '🎯',
                'status': status,
                'type': 'quiz_attempt'
            })
        
        # Recent organization activities (if applicable)
        if hasattr(Organization, 'created_at'):
            recent_orgs = Organization.objects.filter(
                created_at__gte=date_threshold
            )[:5]
            
            for org in recent_orgs:
                activities.append({
                    'user': 'Admin',
                    'action': f'created organization "{org.name}"',
                    'timestamp': org.created_at.isoformat(),
                    'icon': '🏢',
                    'status': 'success',
                    'type': 'organization_creation'
                })
        
        # Sort all activities by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response({
            'activities': activities[:25],  # Return latest 25 activities
            'total_count': len(activities)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching recent activity: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_overview(request):
    """Get system overview statistics"""
    if request.user.profile.role != 'admin':
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Quiz statistics
        total_quizzes = Quiz.objects.count()
        active_quizzes = Quiz.objects.filter(is_active=True).count()
        
        # Organization statistics
        total_organizations = Organization.objects.count()
        active_organizations = Organization.objects.filter(is_active=True).count()
        
        # Attempt statistics
        total_attempts = QuizAttempt.objects.count()
        completed_attempts = QuizAttempt.objects.filter(status='completed').count()
        
        return Response({
            'users': {
                'total': total_users,
                'active': active_users,
                'inactive': total_users - active_users
            },
            'quizzes': {
                'total': total_quizzes,
                'active': active_quizzes,
                'inactive': total_quizzes - active_quizzes
            },
            'organizations': {
                'total': total_organizations,
                'active': active_organizations,
                'inactive': total_organizations - active_organizations
            },
            'attempts': {
                'total': total_attempts,
                'completed': completed_attempts,
                'in_progress': total_attempts - completed_attempts
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching system overview: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
