"""
Updated API Views that work with the actual Django models
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from apps.quizzes.models import Quiz, Question, Choice
from apps.authentication.models import UserProfile
from apps.organizations.models import Organization


@api_view(['GET'])
def get_dashboard_stats(request):
    """Get dashboard statistics"""
    try:
        stats = {
            'total_quizzes': Quiz.objects.filter(is_active=True).count(),
            'total_students': User.objects.filter(is_active=True).count(),
            'total_questions': Question.objects.count(),
            'total_organizations': Organization.objects.count(),
            'active_users': UserProfile.objects.filter(status='active').count(),
        }
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_all_quizzes(request):
    """Get all active quizzes"""
    try:
        quizzes = Quiz.objects.filter(is_active=True).select_related('created_by')
        quiz_list = []
        
        for quiz in quizzes:
            quiz_data = {
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'duration_minutes': quiz.duration_minutes,
                'passing_score': quiz.passing_score,
                'quiz_type': quiz.quiz_type,
                'question_count': quiz.questions.count(),
                'created_by': quiz.created_by.get_full_name() or quiz.created_by.username,
                'created_at': quiz.created_at.isoformat() if hasattr(quiz, 'created_at') else None
            }
            quiz_list.append(quiz_data)
        
        return Response({'quizzes': quiz_list}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_quiz_details(request, quiz_id):
    """Get detailed quiz information including questions and choices"""
    try:
        quiz = Quiz.objects.get(id=quiz_id, is_active=True)
        
        questions = []
        for question in quiz.questions.all().prefetch_related('choices'):
            choices = []
            for choice in question.choices.all():
                choices.append({
                    'id': choice.id,
                    'text': choice.choice_text,
                    'order': choice.order
                })
            
            questions.append({
                'id': question.id,
                'text': question.question_text,
                'type': question.question_type,
                'marks': question.marks,
                'order': question.order,
                'choices': choices
            })
        
        quiz_data = {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'duration_minutes': quiz.duration_minutes,
            'passing_score': quiz.passing_score,
            'quiz_type': quiz.quiz_type,
            'created_by': quiz.created_by.get_full_name() or quiz.created_by.username,
            'questions': questions
        }
        
        return Response({'quiz': quiz_data}, status=status.HTTP_200_OK)
        
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_user_profile(request):
    """Get current user profile"""
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        profile = UserProfile.objects.get(user=request.user)
        user_data = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'full_name': profile.full_name,
            'role': profile.role,
            'organization': profile.organization.name if profile.organization else None,
            'is_active': profile.is_active
        }
        return Response(user_data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        # Create a basic profile if it doesn't exist
        user_data = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'role': 'student',  # Default role
            'organization': None,
            'is_active': True
        }
        return Response(user_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def login_view(request):
    """Custom login view"""
    from django.contrib.auth import authenticate, login
    from rest_framework_simplejwt.tokens import RefreshToken
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    if user:
        if user.is_active:
            login(request, user)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Get user profile
            try:
                profile = UserProfile.objects.get(user=user)
                role = profile.role
                full_name = profile.full_name
                organization = profile.organization.name if profile.organization else None
            except UserProfile.DoesNotExist:
                role = 'admin' if user.is_superuser else 'student'
                full_name = f"{user.first_name} {user.last_name}".strip()
                organization = None
            
            return Response({
                'access': str(access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': full_name,
                    'role': role,
                    'organization': organization
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Account is disabled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
