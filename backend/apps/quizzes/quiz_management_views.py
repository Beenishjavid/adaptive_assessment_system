"""
Quiz Management API Views - Complete CRUD operations
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Avg, Q
from apps.quizzes.models import Quiz, Question, Choice, Topic
from apps.results.models import QuizAttempt, QuizAnswer
from apps.authentication.models import UserProfile
from apps.organizations.models import Organization
from apps.groups.models import Group
import json


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quiz(request):
    """Create a new quiz"""
    try:
        data = request.data
        user = request.user
        
        # Check if user can create quizzes
        if not (user.is_staff or hasattr(user, 'profile') and user.profile.role in ['instructor', 'admin']):
            return Response(
                {'error': 'You do not have permission to create quizzes'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        with transaction.atomic():
            # Create quiz
            quiz = Quiz.objects.create(
                title=data.get('title'),
                description=data.get('description', ''),
                duration_minutes=data.get('duration_minutes', 60),
                max_attempts=data.get('max_attempts', 1),
                passing_score=data.get('passing_score', 70),
                quiz_type=data.get('quiz_type', 'assessment'),
                visibility=data.get('visibility', 'public'),
                randomize_questions=data.get('randomize_questions', False),
                allow_review=data.get('allow_review', True),
                created_by=user,
                is_active=True
            )
            
            # Add questions if provided
            questions_data = data.get('questions', [])
            for idx, question_data in enumerate(questions_data):
                question = Question.objects.create(
                    quiz=quiz,
                    question_text=question_data.get('question_text'),
                    question_type=question_data.get('question_type', 'multiple_choice'),
                    marks=question_data.get('marks', 1),
                    order=idx + 1
                )
                
                # Add choices for MCQ questions
                if question_data.get('question_type') in ['multiple_choice', 'true_false']:
                    choices_data = question_data.get('choices', [])
                    for choice_idx, choice_data in enumerate(choices_data):
                        Choice.objects.create(
                            question=question,
                            choice_text=choice_data.get('choice_text'),
                            is_correct=choice_data.get('is_correct', False),
                            order=choice_idx + 1
                        )
        
        return Response({
            'message': 'Quiz created successfully',
            'quiz_id': quiz.id,
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'duration_minutes': quiz.duration_minutes,
                'question_count': quiz.questions.count()
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Error creating quiz: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_quizzes(request):
    """Get quizzes created by the current user"""
    try:
        user = request.user
        quizzes = Quiz.objects.filter(created_by=user).order_by('-created_at')
        
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
                'attempt_count': QuizAttempt.objects.filter(quiz=quiz).count(),
                'is_active': quiz.is_active,
                'created_at': quiz.created_at.isoformat(),
                'visibility': quiz.visibility
            }
            quiz_list.append(quiz_data)
        
        return Response({'quizzes': quiz_list}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching quizzes: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_quiz(request, quiz_id):
    """Update an existing quiz including questions"""
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
        data = request.data
        
        with transaction.atomic():
            # Update quiz fields with proper null handling
            quiz.title = data.get('title', quiz.title)
            quiz.description = data.get('description', quiz.description)
            
            # Handle nullable integer fields - SQL Server requires NOT NULL values with defaults
            duration_minutes = data.get('duration_minutes')
            if duration_minutes is None or duration_minutes == '':
                # Keep existing value or use default
                quiz.duration_minutes = quiz.duration_minutes or 60
            else:
                try:
                    quiz.duration_minutes = int(duration_minutes)
                except (ValueError, TypeError):
                    quiz.duration_minutes = 60
            
            max_attempts = data.get('max_attempts')
            if max_attempts is None or max_attempts == '':
                # Keep existing value or use default
                quiz.max_attempts = quiz.max_attempts or 1
            else:
                try:
                    quiz.max_attempts = int(max_attempts)
                except (ValueError, TypeError):
                    quiz.max_attempts = 1
            
            passing_score = data.get('passing_score')
            if passing_score is None or passing_score == '':
                # Keep existing value or use default
                quiz.passing_score = quiz.passing_score or 60
            else:
                try:
                    quiz.passing_score = int(passing_score)
                except (ValueError, TypeError):
                    quiz.passing_score = 60
            quiz.quiz_type = data.get('quiz_type', quiz.quiz_type)
            quiz.visibility = data.get('visibility', quiz.visibility)
            quiz.randomize_questions = data.get('randomize_questions', quiz.randomize_questions)
            quiz.allow_review = data.get('allow_review', quiz.allow_review)
            quiz.is_active = data.get('is_active', quiz.is_active)
            quiz.save()
            
            # Update questions if provided (optional for status-only updates)
            if 'questions' in data and data['questions'] is not None:
                # Get existing question IDs
                existing_question_ids = set(quiz.questions.values_list('id', flat=True))
                updated_question_ids = set()
                
                for question_data in data['questions']:
                    question_id = question_data.get('id')
                    
                    # Update existing question or create new one
                    if question_id and question_id in existing_question_ids:
                        # Update existing question
                        question = Question.objects.get(id=question_id, quiz=quiz)
                        question.question_text = question_data.get('question_text', question.question_text)
                        question.question_type = question_data.get('question_type', question.question_type)
                        question.marks = question_data.get('marks', question.marks)
                        # Note: explanation field may not exist in current model
                        question.save()
                        updated_question_ids.add(question_id)
                        
                        # Update choices for this question
                        if 'choices' in question_data and question_data['question_type'] in ['multiple_choice', 'true_false']:
                            # Delete existing choices
                            question.choices.all().delete()
                            
                            # Create new choices
                            for choice_data in question_data['choices']:
                                if choice_data.get('choice_text', '').strip():  # Only create non-empty choices
                                    Choice.objects.create(
                                        question=question,
                                        choice_text=choice_data['choice_text'],
                                        is_correct=choice_data.get('is_correct', False)
                                    )
                    
                    else:
                        # Create new question (for questions with temporary IDs or no ID)
                        question = Question.objects.create(
                            quiz=quiz,
                            question_text=question_data['question_text'],
                            question_type=question_data.get('question_type', 'multiple_choice'),
                            marks=question_data.get('marks', 1)
                        )
                        
                        # Create choices for new question
                        if 'choices' in question_data and question_data['question_type'] in ['multiple_choice', 'true_false']:
                            for choice_data in question_data['choices']:
                                if choice_data.get('choice_text', '').strip():  # Only create non-empty choices
                                    Choice.objects.create(
                                        question=question,
                                        choice_text=choice_data['choice_text'],
                                        is_correct=choice_data.get('is_correct', False)
                                    )
                
                # Delete questions that were removed (not in the updated list)
                questions_to_delete = existing_question_ids - updated_question_ids
                if questions_to_delete:
                    Question.objects.filter(id__in=questions_to_delete, quiz=quiz).delete()
        
        return Response({
            'message': 'Quiz updated successfully',
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'is_active': quiz.is_active,
                'question_count': quiz.questions.count()
            }
        }, status=status.HTTP_200_OK)
        
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found or you do not have permission to edit it'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Quiz update error: {error_traceback}")  # Debug logging
        return Response(
            {'error': f'Error updating quiz: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_quiz(request, quiz_id):
    """Delete a quiz (soft delete by setting is_active=False)"""
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
        quiz.is_active = False
        quiz.save()
        
        return Response({
            'message': 'Quiz deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found or you do not have permission to delete it'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error deleting quiz: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_quiz_attempt(request, quiz_id):
    """Start a new quiz attempt"""
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
        user = request.user
        
        # Check if user can attempt this quiz
        existing_attempts = QuizAttempt.objects.filter(user=user, quiz=quiz).count()
        if existing_attempts >= quiz.max_attempts:
            return Response(
                {'error': f'You have reached the maximum number of attempts ({quiz.max_attempts}) for this quiz'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's an ongoing attempt
        ongoing_attempt = QuizAttempt.objects.filter(
            user=user, 
            quiz=quiz, 
            status='in_progress'
        ).first()
        
        if ongoing_attempt:
            return Response({
                'message': 'Existing attempt found',
                'attempt_id': ongoing_attempt.id,
                'quiz': {
                    'id': quiz.id,
                    'title': quiz.title,
                    'duration_minutes': quiz.duration_minutes
                }
            }, status=status.HTTP_200_OK)
        
        # Create new attempt
        attempt = QuizAttempt.objects.create(
            user=user,
            quiz=quiz,
            status='in_progress',
            started_at=timezone.now()
        )
        
        return Response({
            'message': 'Quiz attempt started successfully',
            'attempt_id': attempt.id,
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'duration_minutes': quiz.duration_minutes,
                'question_count': quiz.questions.count()
            }
        }, status=status.HTTP_201_CREATED)
        
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error starting quiz attempt: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_for_attempt(request, attempt_id):
    """Get quiz questions for an active attempt"""
    try:
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
        
        if attempt.status != 'in_progress':
            return Response(
                {'error': 'This quiz attempt is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        quiz = attempt.quiz
        questions = quiz.questions.all().order_by('order')
        
        # Check time remaining
        if quiz.duration_minutes:
            time_elapsed = (timezone.now() - attempt.started_at).total_seconds() / 60
            time_remaining = max(0, quiz.duration_minutes - time_elapsed)
            
            if time_remaining <= 0:
                # Auto-submit the quiz
                attempt.status = 'completed'
                attempt.finished_at = timezone.now()
                attempt.save()
                
                return Response(
                    {'error': 'Time limit exceeded. Quiz has been auto-submitted.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            time_remaining = None
        
        questions_data = []
        for question in questions:
            question_data = {
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'marks': question.marks,
                'order': question.order
            }
            
            # Add choices for MCQ questions
            if question.question_type in ['multiple_choice', 'true_false']:
                choices = question.choices.all().order_by('order')
                question_data['choices'] = [
                    {
                        'id': choice.id,
                        'choice_text': choice.choice_text,
                        'order': choice.order
                    }
                    for choice in choices
                ]
            
            questions_data.append(question_data)
        
        return Response({
            'attempt_id': attempt.id,
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'duration_minutes': quiz.duration_minutes,
                'time_remaining': time_remaining
            },
            'questions': questions_data
        }, status=status.HTTP_200_OK)
        
    except QuizAttempt.DoesNotExist:
        return Response(
            {'error': 'Quiz attempt not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error fetching quiz: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz_answer(request, attempt_id):
    """Submit an answer for a question"""
    try:
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
        
        if attempt.status != 'in_progress':
            return Response(
                {'error': 'This quiz attempt is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = request.data
        question_id = data.get('question_id')
        choice_id = data.get('choice_id')
        
        question = get_object_or_404(Question, id=question_id, quiz=attempt.quiz)
        
        # Save or update answer
        answer, created = QuizAnswer.objects.get_or_create(
            attempt=attempt,
            question=question,
            defaults={'answered_at': timezone.now()}
        )
        
        if question.question_type in ['multiple_choice', 'true_false']:
            # For MCQ, save the selected choice
            if choice_id:
                choice = get_object_or_404(Choice, id=choice_id, question=question)
                answer.selected_choice = choice
                answer.is_correct = choice.is_correct
        
        answer.save()
        
        return Response({
            'message': 'Answer saved successfully',
            'question_id': question_id,
            'is_correct': answer.is_correct,
            'saved_at': answer.answered_at.isoformat()
        }, status=status.HTTP_200_OK)
        
    except (QuizAttempt.DoesNotExist, Question.DoesNotExist, Choice.DoesNotExist):
        return Response(
            {'error': 'Invalid quiz attempt, question, or choice'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error saving answer: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request, attempt_id):
    """Submit the entire quiz"""
    try:
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
        
        if attempt.status != 'in_progress':
            return Response(
                {'error': 'This quiz attempt is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark attempt as completed
        attempt.status = 'completed'
        attempt.finished_at = timezone.now()
        
        # Calculate score
        total_points = 0
        earned_points = 0
        
        for question in attempt.quiz.questions.all():
            total_points += question.marks
            
            try:
                answer = QuizAnswer.objects.get(attempt=attempt, question=question)
                
                if question.question_type in ['multiple_choice', 'true_false']:
                    if answer.selected_choice and answer.selected_choice.is_correct:
                        earned_points += question.marks
                        answer.is_correct = True
                    else:
                        answer.is_correct = False
                    answer.save()
                
            except QuizAnswer.DoesNotExist:
                # No answer submitted for this question
                pass
        
        # Calculate percentage score
        if total_points > 0:
            percentage = (earned_points / total_points) * 100
        else:
            percentage = 0
        
        attempt.score = earned_points
        attempt.total_marks = total_points
        attempt.percentage = percentage
        attempt.save()
        
        return Response({
            'message': 'Quiz submitted successfully',
            'result': {
                'attempt_id': attempt.id,
                'score': earned_points,
                'earned_points': earned_points,
                'total_points': total_points,
                'percentage': percentage,
                'passed': percentage >= attempt.quiz.passing_score,
                'passing_score': attempt.quiz.passing_score
            }
        }, status=status.HTTP_200_OK)
        
    except QuizAttempt.DoesNotExist:
        return Response(
            {'error': 'Quiz attempt not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error submitting quiz: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_result(request, attempt_id):
    """Get detailed quiz results"""
    try:
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
        
        if attempt.status != 'completed':
            return Response(
                {'error': 'Quiz not yet completed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        answers = QuizAnswer.objects.filter(attempt=attempt).select_related(
            'question', 'selected_choice'
        ).order_by('question__order')
        
        answers_data = []
        for answer in answers:
            answer_data = {
                'question': {
                    'id': answer.question.id,
                    'text': answer.question.question_text,
                    'question_type': answer.question.question_type,
                    'points': answer.question.marks
                },
                'is_correct': answer.is_correct
            }
            
            if answer.selected_choice:
                answer_data['selected_choice'] = {
                    'id': answer.selected_choice.id,
                    'text': answer.selected_choice.choice_text,
                    'is_correct': answer.selected_choice.is_correct
                }
            
            # Add correct answers for review
            if answer.question.question_type in ['multiple_choice', 'true_false']:
                correct_choices = answer.question.choices.filter(is_correct=True)
                answer_data['correct_choices'] = [
                    {
                        'id': choice.id,
                        'text': choice.choice_text
                    }
                    for choice in correct_choices
                ]
            
            answers_data.append(answer_data)
        
        return Response({
            'attempt': {
                'id': attempt.id,
                'quiz_title': attempt.quiz.title,
                'score': attempt.score,
                'total_marks': attempt.total_marks,
                'percentage': attempt.percentage,
                'passed': attempt.percentage >= attempt.quiz.passing_score,
                'passing_score': attempt.quiz.passing_score,
                'started_at': attempt.started_at.isoformat(),
                'finished_at': attempt.finished_at.isoformat() if attempt.finished_at else None,
                'duration_minutes': attempt.quiz.duration_minutes
            },
            'answers': answers_data
        }, status=status.HTTP_200_OK)
        
    except QuizAttempt.DoesNotExist:
        return Response(
            {'error': 'Quiz attempt not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error fetching quiz result: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_quiz_attempts(request):
    """Get all quiz attempts for the current user"""
    try:
        user = request.user
        attempts = QuizAttempt.objects.filter(user=user).select_related('quiz').order_by('-started_at')
        
        attempts_data = []
        for attempt in attempts:
            attempt_data = {
                'id': attempt.id,
                'quiz': {
                    'id': attempt.quiz.id,
                    'title': attempt.quiz.title,
                    'quiz_type': attempt.quiz.quiz_type
                },
                'score': attempt.score,
                'status': attempt.status,
                'started_at': attempt.started_at.isoformat(),
                'finished_at': attempt.finished_at.isoformat() if attempt.finished_at else None,
                'passed': attempt.score >= attempt.quiz.passing_score if attempt.score is not None else None
            }
            attempts_data.append(attempt_data)
        
        return Response({'attempts': attempts_data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching quiz attempts: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_results(request):
    """Get detailed quiz results for the current user"""
    try:
        user = request.user
        attempts = QuizAttempt.objects.filter(
            user=user, 
            status='completed'
        ).select_related('quiz').order_by('-finished_at')
        
        results = []
        for attempt in attempts:
            # Calculate percentage
            percentage = 0
            if attempt.total_marks and attempt.total_marks > 0:
                percentage = round((attempt.score / attempt.total_marks) * 100, 1)
            
            result_data = {
                'attempt_id': attempt.id,
                'quiz_title': attempt.quiz.title,
                'quiz_id': attempt.quiz.id,
                'score': attempt.score or 0,
                'total_marks': attempt.total_marks or 0,
                'percentage': percentage,
                'passing_score': attempt.quiz.passing_score,
                'completed_at': attempt.finished_at.isoformat() if attempt.finished_at else None,
                'attempt_number': QuizAttempt.objects.filter(
                    user=user, 
                    quiz=attempt.quiz,
                    finished_at__lt=attempt.finished_at
                ).count() + 1,
                'total_questions': attempt.quiz.questions.count(),
                'quiz_type': attempt.quiz.quiz_type
            }
            results.append(result_data)
        
        return Response({'results': results}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching quiz results: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_instructor_stats(request):
    """Get instructor dashboard statistics"""
    try:
        user = request.user
        
        # Get instructor's quizzes
        my_quizzes = Quiz.objects.filter(created_by=user, is_active=True)
        quiz_ids = list(my_quizzes.values_list('id', flat=True))
        
        # Get attempts on instructor's quizzes
        attempts = QuizAttempt.objects.filter(
            quiz_id__in=quiz_ids,
            status='completed'
        )
        
        # Calculate stats
        total_attempts = attempts.count()
        if total_attempts > 0:
            total_score = sum(attempt.score or 0 for attempt in attempts)
            average_score = total_score / total_attempts
            
            # Get active students (students who attempted in last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            active_students = attempts.filter(
                started_at__gte=thirty_days_ago
            ).values('user').distinct().count()
        else:
            average_score = 0
            active_students = 0
        
        stats = {
            'total_attempts': total_attempts,
            'average_score': round(average_score, 1),
            'active_students': active_students,
            'total_quizzes': my_quizzes.count()
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching instructor stats: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_instructor_quiz_attempts(request):
    """Get all student attempts for instructor's quizzes with detailed analytics"""
    try:
        user = request.user
        
        # Check if user is instructor
        if not hasattr(user, 'profile') or user.profile.role != 'instructor':
            return Response(
                {'error': 'Access denied. Only instructors can view this data.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get optional quiz filter
        quiz_id = request.GET.get('quiz_id')
        
        # Get instructor's quizzes
        my_quizzes_query = Quiz.objects.filter(created_by=user, is_active=True)
        if quiz_id:
            my_quizzes_query = my_quizzes_query.filter(id=quiz_id)
        
        my_quizzes = my_quizzes_query
        quiz_ids = list(my_quizzes.values_list('id', flat=True))
        
        if not quiz_ids:
            return Response({
                'quizzes': [],
                'attempts': [],
                'analytics': {
                    'total_attempts': 0,
                    'total_students': 0,
                    'average_score': 0,
                    'completion_rate': 0
                }
            })
        
        # Get all attempts for these quizzes
        attempts = QuizAttempt.objects.filter(
            quiz_id__in=quiz_ids
        ).select_related('user', 'quiz').order_by('-started_at')
        
        # Get quiz details for dropdown
        quiz_options = []
        for quiz in my_quizzes:
            quiz_options.append({
                'id': quiz.id,
                'title': quiz.title,
                'quiz_type': quiz.quiz_type,
                'is_active': quiz.is_active,
                'created_at': quiz.created_at.isoformat(),
                'attempt_count': attempts.filter(quiz=quiz).count(),
                'avg_score': attempts.filter(quiz=quiz, status='completed').aggregate(
                    avg_score=Avg('score')
                )['avg_score'] or 0
            })        # Process attempts data
        attempts_data = []
        for attempt in attempts:
            # Get answer details for this attempt
            answers = QuizAnswer.objects.filter(attempt=attempt).select_related('question')
            
            correct_answers = sum(1 for answer in answers if answer.is_correct)
            total_questions = answers.count()
            
            attempts_data.append({
                'id': attempt.id,
                'student': {
                    'id': attempt.user.id,
                    'username': attempt.user.username,
                    'full_name': attempt.user.get_full_name() or attempt.user.username,
                    'email': attempt.user.email
                },
                'quiz': {
                    'id': attempt.quiz.id,
                    'title': attempt.quiz.title,
                    'quiz_type': attempt.quiz.quiz_type,
                    'total_questions': attempt.quiz.questions.count()
                },
                'score': attempt.score,
                'status': attempt.status,
                'started_at': attempt.started_at.isoformat(),
                'completed_at': attempt.finished_at.isoformat() if attempt.finished_at else None,
                'time_taken': str(attempt.finished_at - attempt.started_at) if attempt.finished_at else None,
                'correct_answers': correct_answers,
                'total_answers': total_questions,
                'accuracy': round((correct_answers / total_questions * 100), 2) if total_questions > 0 else 0
            })
        
        # Calculate analytics
        completed_attempts = attempts.filter(status='completed')
        total_attempts = attempts.count()
        total_students = attempts.values('user').distinct().count()
        
        if completed_attempts.exists():
            avg_score = completed_attempts.aggregate(avg=Avg('score'))['avg'] or 0
            completion_rate = (completed_attempts.count() / total_attempts * 100) if total_attempts > 0 else 0
        else:
            avg_score = 0
            completion_rate = 0
        
        analytics = {
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts.count(),
            'total_students': total_students,
            'average_score': round(avg_score, 2),
            'completion_rate': round(completion_rate, 2),
            'quiz_count': len(quiz_options)
        }
        
        return Response({
            'quizzes': quiz_options,
            'attempts': attempts_data,
            'analytics': analytics
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching quiz attempts: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_preview(request, quiz_id):
    """Get quiz details for preview (read-only view)"""
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Check if user can preview this quiz
        if not (quiz.created_by == request.user or request.user.is_staff or 
                (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')):
            return Response(
                {'error': 'You do not have permission to preview this quiz'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get questions with choices
        questions = []
        for question in quiz.questions.all():
            question_data = {
                'id': question.id,
                'text': question.question_text,
                'question_type': question.question_type,
                'points': question.marks,
                'explanation': '',  # Explanation field not available in current model
                'choices': []
            }
            
            for choice in question.choices.all():
                question_data['choices'].append({
                    'id': choice.id,
                    'text': choice.choice_text,
                    'is_correct': choice.is_correct
                })
            
            questions.append(question_data)
        
        quiz_data = {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'duration_minutes': quiz.duration_minutes,
            'max_attempts': quiz.max_attempts,
            'passing_score': quiz.passing_score,
            'quiz_type': quiz.quiz_type,
            'visibility': quiz.visibility,
            'randomize_questions': quiz.randomize_questions,
            'allow_review': quiz.allow_review,
            'is_active': quiz.is_active,
            'created_at': quiz.created_at,
            'created_by': quiz.created_by.username,
            'questions': questions,
            'question_count': len(questions),
            'total_points': sum(q['points'] for q in questions)
        }
        
        return Response(quiz_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching quiz preview: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_for_editing(request, quiz_id):
    """Get quiz details with all data needed for editing"""
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Check if user can edit this quiz
        if not (quiz.created_by == request.user or request.user.is_staff or 
                (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')):
            return Response(
                {'error': 'You do not have permission to edit this quiz'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get questions with choices for editing
        questions = []
        for question in quiz.questions.all():
            question_data = {
                'id': question.id,
                'text': question.question_text,
                'question_type': question.question_type,
                'points': question.marks,
                'explanation': '',  # Explanation field not available in current model
                'choices': []
            }
            
            for choice in question.choices.all():
                question_data['choices'].append({
                    'id': choice.id,
                    'text': choice.choice_text,
                    'is_correct': choice.is_correct
                })
            
            questions.append(question_data)
        
        quiz_data = {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'duration_minutes': quiz.duration_minutes,
            'max_attempts': quiz.max_attempts,
            'passing_score': quiz.passing_score,
            'quiz_type': quiz.quiz_type,
            'visibility': quiz.visibility,
            'randomize_questions': quiz.randomize_questions,
            'allow_review': quiz.allow_review,
            'is_active': quiz.is_active,
            'questions': questions
        }
        
        return Response(quiz_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching quiz for editing: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_results_analytics(request, quiz_id):
    """Get detailed analytics and results for a specific quiz"""
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Check if user can view results for this quiz
        if not (quiz.created_by == request.user or request.user.is_staff or 
                (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')):
            return Response(
                {'error': 'You do not have permission to view results for this quiz'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all attempts for this quiz
        attempts = QuizAttempt.objects.filter(quiz=quiz).select_related('user')
        
        # Basic statistics
        total_attempts = attempts.count()
        completed_attempts = attempts.filter(status='completed')
        passed_attempts = completed_attempts.filter(percentage__gte=quiz.passing_score)
        
        if completed_attempts.exists():
            avg_score = completed_attempts.aggregate(Avg('percentage'))['percentage__avg']
            max_score = completed_attempts.order_by('-percentage').first().percentage
            min_score = completed_attempts.order_by('percentage').first().percentage
        else:
            avg_score = max_score = min_score = 0
        
        # Recent attempts (last 10)
        recent_attempts = []
        for attempt in attempts.filter(status='completed').order_by('-finished_at')[:10]:
            recent_attempts.append({
                'id': attempt.id,
                'user': attempt.user.get_full_name() or attempt.user.username,
                'score': attempt.percentage or 0,
                'passed': (attempt.percentage or 0) >= quiz.passing_score,
                'completed_at': attempt.finished_at,
                'duration': attempt.time_taken_minutes * 60 if attempt.time_taken_minutes else 0
            })
        
        # Score distribution
        score_ranges = {
            '0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0
        }
        
        for attempt in completed_attempts:
            score = attempt.percentage or 0
            if score <= 20:
                score_ranges['0-20'] += 1
            elif score <= 40:
                score_ranges['21-40'] += 1
            elif score <= 60:
                score_ranges['41-60'] += 1
            elif score <= 80:
                score_ranges['61-80'] += 1
            else:
                score_ranges['81-100'] += 1
        
        # Question analytics
        questions_analytics = []
        for question in quiz.questions.all():
            question_answers = QuizAnswer.objects.filter(
                question=question,
                attempt__in=completed_attempts
            )
            
            total_answers = question_answers.count()
            if total_answers > 0:
                correct_answers = question_answers.filter(is_correct=True).count()
                accuracy = (correct_answers / total_answers) * 100
            else:
                accuracy = 0
            
            questions_analytics.append({
                'question_id': question.id,
                'question_text': question.question_text[:100] + '...' if len(question.question_text) > 100 else question.question_text,
                'total_answers': total_answers,
                'accuracy': round(accuracy, 1),
                'points': question.marks
            })
        
        analytics_data = {
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'passing_score': quiz.passing_score,
                'total_questions': quiz.questions.count()
            },
            'statistics': {
                'total_attempts': total_attempts,
                'completed_attempts': completed_attempts.count(),
                'passed_attempts': passed_attempts.count(),
                'pass_rate': round((passed_attempts.count() / completed_attempts.count() * 100), 1) if completed_attempts.count() > 0 else 0,
                'average_score': round(avg_score, 1) if avg_score else 0,
                'highest_score': max_score,
                'lowest_score': min_score
            },
            'recent_attempts': recent_attempts,
            'score_distribution': score_ranges,
            'questions_analytics': questions_analytics
        }
        
        return Response(analytics_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching quiz analytics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
