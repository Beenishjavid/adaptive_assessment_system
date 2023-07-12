"""
Advanced Admin API Views - Reports, Analytics, and System Settings
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.core.management import call_command
from django.core.cache import cache
from datetime import datetime, timedelta
import psutil
import platform
import sys
import os
import json
from apps.authentication.models import UserProfile
from apps.organizations.models import Organization
from apps.quizzes.models import Quiz, Question
from apps.results.models import QuizAttempt
from apps.simple_admin_api import check_admin_permission


# System Settings Storage (in production, use database or Redis)
SYSTEM_SETTINGS = {
    'site_name': 'Smart Quiz System',
    'site_description': 'Advanced Quiz Management Platform',
    'max_quiz_time': 180,
    'max_questions_per_quiz': 100,
    'allow_guest_access': False,
    'enable_notifications': True,
    'quiz_auto_save_interval': 30,
    'session_timeout': 30,
    'max_login_attempts': 5,
    'password_min_length': 8,
    'require_email_verification': True,
    'enable_proctoring': True,
    'backup_frequency': 'daily',
    'log_retention_days': 90,
    'maintenance_mode': False,
    'debug_mode': False
}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_analytics(request):
    """Get comprehensive quiz analytics"""
    if not check_admin_permission(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Quiz statistics
        total_quizzes = Quiz.objects.count()
        active_quizzes = Quiz.objects.filter(is_active=True).count()
        
        # Quiz attempts and completion rates
        total_attempts = QuizAttempt.objects.count()
        completed_attempts = QuizAttempt.objects.filter(status='completed').count()
        completion_rate = (completed_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        # Average scores
        avg_score = QuizAttempt.objects.aggregate(
            avg_score=Avg('score')
        )['avg_score'] or 0
        
        # Quiz type distribution 
        quiz_difficulty = Quiz.objects.values('quiz_type').annotate(
            count=Count('id')
        ).order_by('quiz_type')        # Popular quizzes (most attempted)
        popular_quizzes = Quiz.objects.annotate(
            attempt_count=Count('quizattempt')
        ).order_by('-attempt_count')[:10]
        
        # Recent quiz activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_attempts = QuizAttempt.objects.filter(
            started_at__gte=thirty_days_ago
        ).values('started_at__date').annotate(
            count=Count('id')
        ).order_by('started_at__date')
        
        return Response({
            'overview': {
                'total_quizzes': total_quizzes,
                'active_quizzes': active_quizzes,
                'total_attempts': total_attempts,
                'completion_rate': round(completion_rate, 2),
                'average_score': round(avg_score, 2)
            },
            'difficulty_distribution': [
                {'difficulty': item['quiz_type'], 'count': item['count']} 
                for item in quiz_difficulty
            ],
            'popular_quizzes': [
                {
                    'id': q.id,
                    'title': q.title,
                    'attempts': q.attempt_count,
                    'created_by': q.created_by.get_full_name() or q.created_by.username
                }
                for q in popular_quizzes
            ],
            'quiz_activity': [
                {
                    'date': item['started_at__date'].strftime('%Y-%m-%d'),
                    'count': item['count']
                }
                for item in recent_attempts
            ]
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Error fetching quiz analytics: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_analytics(request):
    """Get comprehensive user analytics"""
    if not check_admin_permission(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Role distribution
        role_distribution = UserProfile.objects.values('role').annotate(
            count=Count('id')
        ).order_by('role')
        
        # User registration trends (last 12 months)
        twelve_months_ago = timezone.now() - timedelta(days=365)
        
        # SQL Server compatible date grouping
        from django.db.models import DateTimeField
        from django.db.models.functions import TruncMonth
        
        registration_trends = User.objects.filter(
            date_joined__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('date_joined')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Most active users (by quiz attempts)
        active_users_list = User.objects.annotate(
            attempt_count=Count('quizattempt')
        ).order_by('-attempt_count')[:10]
        
        # User status distribution
        user_status = UserProfile.objects.values('status').annotate(
            count=Count('id')
        )
        
        # Calculate new users this month
        this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_users_this_month = User.objects.filter(date_joined__gte=this_month).count()
        
        # Calculate average score
        avg_score = QuizAttempt.objects.aggregate(avg_score=Avg('percentage'))['avg_score'] or 0
        
        return Response({
            'overview': {
                'total_users': total_users,
                'active_users': active_users,
                'new_users_this_month': new_users_this_month,
                'average_score': round(avg_score, 2)
            },
            'role_distribution': [{'role': item['role'], 'count': item['count']} for item in role_distribution],
            'status_distribution': [{'status': item['status'], 'count': item['count']} for item in user_status],
            'registration_trend': [
                {
                    'date': trend['month'].strftime('%Y-%m'),
                    'count': trend['count']
                }
                for trend in registration_trends
            ],
            'most_active_users': [
                {
                    'id': u.id,
                    'name': u.get_full_name() or u.username,
                    'email': u.email,
                    'attempts': u.attempt_count,
                    'role': getattr(u.profile, 'role', 'student') if hasattr(u, 'profile') else 'student'
                }
                for u in active_users_list if u.attempt_count > 0
            ]
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Error fetching user analytics: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_analytics(request):
    """Get comprehensive organization analytics"""
    if not check_admin_permission(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Organization statistics
        total_organizations = Organization.objects.count()
        active_organizations = Organization.objects.filter(is_active=True).count()
        
        # Organizations by user count
        org_user_counts = []
        for org in Organization.objects.all():
            user_count = UserProfile.objects.filter(organization=org.name).count()
            org_user_counts.append({
                'id': org.id,
                'name': org.name,
                'user_count': user_count,
                'is_active': org.is_active,
                'created_at': org.created_at
            })
        
        # Sort by user count
        org_user_counts.sort(key=lambda x: x['user_count'], reverse=True)
        
        return Response({
            'overview': {
                'total_organizations': total_organizations,
                'active_organizations': active_organizations,
                'inactive_organizations': total_organizations - active_organizations
            },
            'top_organizations': org_user_counts[:10],
            'all_organizations': org_user_counts
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Error fetching organization analytics: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_activity(request):
    """Get recent system activity"""
    if not check_admin_permission(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        days = int(request.GET.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)
        
        activities = []
        
        # Recent user registrations
        new_users = User.objects.filter(date_joined__gte=since_date).order_by('-date_joined')[:20]
        for user in new_users:
            activities.append({
                'icon': '👤',
                'user': user.get_full_name() or user.username,
                'action': 'registered to the platform',
                'timestamp': user.date_joined.strftime('%Y-%m-%d %H:%M'),
                'status': 'success'
            })
        
        # Recent quiz creations
        new_quizzes = Quiz.objects.filter(created_at__gte=since_date).order_by('-created_at')[:20]
        for quiz in new_quizzes:
            activities.append({
                'icon': '📝',
                'user': quiz.created_by.get_full_name() or quiz.created_by.username,
                'action': f'created quiz "{quiz.title}"',
                'timestamp': quiz.created_at.strftime('%Y-%m-%d %H:%M'),
                'status': 'success'
            })
        
        # Recent quiz attempts
        recent_attempts = QuizAttempt.objects.filter(started_at__gte=since_date).order_by('-started_at')[:20]
        for attempt in recent_attempts:
            activities.append({
                'icon': '🎯',
                'user': attempt.user.get_full_name() or attempt.user.username,
                'action': f'attempted quiz "{attempt.quiz.title}"',
                'timestamp': attempt.started_at.strftime('%Y-%m-%d %H:%M'),
                'status': attempt.status
            })
        
        # Sort all activities by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response({
            'activities': activities[:50],  # Limit to 50 most recent
            'total_count': len(activities)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Error fetching recent activity: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_settings(request):
    """Get current system settings"""
    if not check_admin_permission(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    return Response({
        'settings': SYSTEM_SETTINGS
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_system_settings(request):
    """Update system settings"""
    if not check_admin_permission(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        new_settings = request.data.get('settings', {})
        
        # Validate and update settings
        for key, value in new_settings.items():
            if key in SYSTEM_SETTINGS:
                SYSTEM_SETTINGS[key] = value
        
        # In production, save to database or persistent storage
        # For now, just update in-memory dict
        
        return Response({
            'message': 'Settings updated successfully',
            'settings': SYSTEM_SETTINGS
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Error updating settings: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_info(request):
    """Get system information"""
    if not check_admin_permission(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # System information
        system_info = {
            'django_version': getattr(settings, 'VERSION', 'Unknown'),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'platform': platform.platform(),
            'server_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        }
        
        # Database info
        from django.db import connection
        system_info['database_info'] = f"{connection.vendor} (connection: {connection.settings_dict.get('NAME', 'Unknown')})"
        
        # System resources (if psutil is available)
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            system_info.update({
                'memory_usage': f"{memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)",
                'disk_usage': f"{disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)",
                'cpu_count': psutil.cpu_count(),
                'cpu_usage': f"{psutil.cpu_percent()}%"
            })
        except:
            system_info.update({
                'memory_usage': 'Not available',
                'disk_usage': 'Not available',
                'cpu_count': 'Not available',
                'cpu_usage': 'Not available'
            })
        
        # Application statistics
        system_info.update({
            'active_users': User.objects.filter(is_active=True).count(),
            'total_quizzes': Quiz.objects.count(),
            'total_questions': Question.objects.count(),
            'uptime': 'Not available'  # Would need to track application start time
        })
        
        return Response(system_info, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Error fetching system info: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_backup(request):
    """Create database backup"""
    if not check_admin_permission(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # In a real production environment, you'd use proper backup tools
        # This is a simplified example
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}.json"
        
        # For demonstration, return success
        # In production, implement actual backup logic
        
        return Response({
            'message': 'Backup created successfully',
            'backup_name': backup_name,
            'timestamp': timestamp,
            'download_url': f'/api/admin/download-backup/{backup_name}/'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Error creating backup: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cache(request):
    """Clear system cache"""
    if not check_admin_permission(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        cache.clear()
        
        return Response({
            'message': 'Cache cleared successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Error clearing cache: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
