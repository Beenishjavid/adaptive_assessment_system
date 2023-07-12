"""
Quiz Views - API endpoints for quiz data
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q, Avg
from django.utils import timezone

from .models import Quiz, Question, Choice, Topic
from .serializers import QuizSerializer, QuestionSerializer, TopicSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_list(request):
    """Get list of quizzes for the authenticated user"""
    user = request.user
    
    # Get quizzes based on user role
    if hasattr(user, 'profile') and user.profile.role == 'instructor':
        # Instructors see their own quizzes
        quizzes = Quiz.objects.filter(created_by=user)
    else:
        # Students see public quizzes and group quizzes they have access to
        user_groups = user.groups_membership.values_list('group_id', flat=True)
        quizzes = Quiz.objects.filter(
            Q(visibility='public') | 
            Q(group_id__in=user_groups) |
            Q(created_by=user)
        )
    
    quizzes = quizzes.filter(is_active=True).select_related('topic', 'created_by', 'group')
    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_detail(request, quiz_id):
    """Get quiz details with questions and choices"""
    try:
        quiz = Quiz.objects.select_related('topic', 'created_by', 'group').get(id=quiz_id)
        
        # Check if user has access to this quiz
        user = request.user
        if quiz.visibility == 'private' and quiz.created_by != user:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        elif quiz.visibility == 'group':
            user_groups = user.groups_membership.values_list('group_id', flat=True)
            if quiz.group_id not in user_groups and quiz.created_by != user:
                return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)
        
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_questions(request, quiz_id):
    """Get questions for a specific quiz"""
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz).prefetch_related('choices').order_by('order')
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
        
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def topics_list(request):
    """Get list of available topics"""
    topics = Topic.objects.filter(is_active=True).order_by('name')
    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for the user"""
    user = request.user
    
    if hasattr(user, 'profile') and user.profile.role == 'instructor':
        # Instructor stats
        total_quizzes = Quiz.objects.filter(created_by=user).count()
        active_quizzes = Quiz.objects.filter(created_by=user, is_active=True).count()
        total_questions = Question.objects.filter(quiz__created_by=user).count()
        
        stats = {
            'role': 'instructor',
            'total_quizzes': total_quizzes,
            'active_quizzes': active_quizzes,
            'total_questions': total_questions,
            'recent_quizzes': QuizSerializer(
                Quiz.objects.filter(created_by=user).order_by('-created_at')[:5], 
                many=True
            ).data
        }
    else:
        # Student stats
        user_groups = user.groups_membership.values_list('group_id', flat=True)
        available_quizzes = Quiz.objects.filter(
            Q(visibility='public') | Q(group_id__in=user_groups),
            is_active=True
        ).count()
        
        # Mock attempt data (you can implement this based on your results models)
        completed_quizzes = 0  # TODO: Implement based on quiz attempts
        average_score = 0  # TODO: Implement based on quiz results
        
        stats = {
            'role': 'student',
            'available_quizzes': available_quizzes,
            'completed_quizzes': completed_quizzes,
            'average_score': average_score,
            'recent_quizzes': QuizSerializer(
                Quiz.objects.filter(
                    Q(visibility='public') | Q(group_id__in=user_groups),
                    is_active=True
                ).order_by('-created_at')[:5], 
                many=True
            ).data
        }
    
    return Response(stats)
