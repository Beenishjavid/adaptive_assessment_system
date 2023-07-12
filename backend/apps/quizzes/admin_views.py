"""
Admin Quiz Statistics API Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.quizzes.models import Quiz, Question, Choice
from apps.results.models import QuizAttempt
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_stats(request):
    """Get quiz statistics for admin dashboard"""
    if request.user.userprofile.role != 'admin':
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        days = int(request.GET.get('days', 30))
        date_threshold = datetime.now() - timedelta(days=days)
        
        # Basic quiz stats
        total_quizzes = Quiz.objects.count()
        active_quizzes = Quiz.objects.filter(is_active=True).count()
        recent_quizzes = Quiz.objects.filter(
            created_at__gte=date_threshold
        ).count() if hasattr(Quiz, 'created_at') else 0
        
        # Quiz attempts stats
        total_attempts = QuizAttempt.objects.count()
        completed_attempts = QuizAttempt.objects.filter(status='completed').count()
        recent_attempts = QuizAttempt.objects.filter(
            started_at__gte=date_threshold
        ).count()
        
        # Average scores
        avg_score = QuizAttempt.objects.filter(
            status='completed',
            score__isnull=False
        ).aggregate(avg_score=Avg('score'))['avg_score'] or 0
        
        # Quiz type distribution
        quiz_types = Quiz.objects.values('quiz_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Most attempted quizzes
        popular_quizzes = Quiz.objects.annotate(
            attempt_count=Count('quizattempt')
        ).filter(attempt_count__gt=0).order_by('-attempt_count')[:5]
        
        popular_quiz_data = []
        for quiz in popular_quizzes:
            quiz_avg = QuizAttempt.objects.filter(
                quiz=quiz,
                status='completed',
                score__isnull=False
            ).aggregate(avg_score=Avg('score'))['avg_score'] or 0
            
            popular_quiz_data.append({
                'title': quiz.title,
                'attempts': quiz.attempt_count,
                'average_score': round(quiz_avg, 1),
                'created_by': quiz.created_by.get_full_name() or quiz.created_by.username
            })
        
        return Response({
            'total_quizzes': total_quizzes,
            'active_quizzes': active_quizzes,
            'recent_quizzes': recent_quizzes,
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts,
            'recent_attempts': recent_attempts,
            'average_score': round(avg_score, 1),
            'quiz_type_distribution': list(quiz_types),
            'popular_quizzes': popular_quiz_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching quiz stats: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_activity(request):
    """Get recent system activity"""
    if request.user.userprofile.role != 'admin':
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        days = int(request.GET.get('days', 30))
        date_threshold = datetime.now() - timedelta(days=days)
        
        activities = []
        
        # Recent quiz creations
        recent_quizzes = Quiz.objects.filter(
            created_at__gte=date_threshold
        ).select_related('created_by')[:10] if hasattr(Quiz, 'created_at') else []
        
        for quiz in recent_quizzes:
            activities.append({
                'user': quiz.created_by.get_full_name() or quiz.created_by.username,
                'action': f'created quiz "{quiz.title}"',
                'timestamp': quiz.created_at.isoformat() if hasattr(quiz, 'created_at') else '',
                'icon': '📝',
                'status': 'success'
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
                'status': status
            })
        
        # Sort all activities by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response({
            'activities': activities[:20]  # Return latest 20 activities
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching recent activity: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
