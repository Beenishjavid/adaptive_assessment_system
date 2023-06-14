from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Quiz, Question, Choice, QuestionBank
from results.models import QuizAttempt, Answer
from users.models import UserProfile

def home(request):
    """Home page - show welcome page for all users"""
    if not request.user.is_authenticated:
        # Show welcome page with login/register options
        context = {
            'title': 'Welcome to Smart Quiz System'
        }
        return render(request, 'quizzes/welcome.html', context)
    
    # For authenticated users, show a home dashboard with navigation options
    try:
        user_profile = request.user.userprofile
        role = user_profile.role
    except UserProfile.DoesNotExist:
        # Create profile for users without one (like superusers)
        if request.user.is_superuser:
            user_profile = UserProfile.objects.create(user=request.user, role='admin')
            role = 'admin'
        elif request.user.is_staff:
            user_profile = UserProfile.objects.create(user=request.user, role='instructor')
            role = 'instructor'
        else:
            user_profile = UserProfile.objects.create(user=request.user, role='student')
            role = 'student'
    
    # Show a dashboard home page with navigation options instead of auto-redirecting
    context = {
        'title': 'Smart Quiz System - Home',
        'user_role': role,
        'user_profile': user_profile
    }
    
    return render(request, 'quizzes/dashboard_home.html', context)

@login_required
def quiz_list(request):
    """Display all available quizzes"""
    now = timezone.now()
    
    # Filter quizzes based on availability and schedule
    quizzes = Quiz.objects.filter(
        is_active=True
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=now)
    ).order_by('-created_at')
    
    # Add availability status to each quiz
    for quiz in quizzes:
        quiz.availability_status = 'available'
        quiz.can_take = True
        
        if quiz.end_date and now > quiz.end_date:
            if quiz.allow_late_submission:
                grace_end = quiz.end_date + timezone.timedelta(minutes=quiz.grace_period_minutes)
                if now <= grace_end:
                    quiz.availability_status = 'late_submission'
                    quiz.can_take = True
                else:
                    quiz.availability_status = 'closed'
                    quiz.can_take = False
            else:
                quiz.availability_status = 'closed'
                quiz.can_take = False
    
    return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})

@login_required
def quiz_detail(request, quiz_id):
    """Show quiz details before taking it"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check availability
    if not quiz.is_available() and not quiz.is_late_submission_allowed():
        messages.error(request, 'This quiz is not currently available.')
        return redirect('quiz_list')
    
    # Check if user already attempted this quiz
    user_attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz)
    can_attempt = user_attempts.count() < quiz.max_attempts
    
    # Check if late submission penalty applies
    late_submission = quiz.is_late_submission_allowed()
    
    context = {
        'quiz': quiz,
        'user_attempts': user_attempts,
        'can_attempt': can_attempt,
        'late_submission': late_submission,
        'late_penalty': quiz.late_submission_penalty if late_submission else 0,
        'title': f'Quiz: {quiz.title}'
    }
    return render(request, 'quizzes/quiz_detail.html', context)

@login_required
def start_quiz(request, quiz_id):
    """Start a new quiz attempt"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check availability
    if not quiz.is_available() and not quiz.is_late_submission_allowed():
        messages.error(request, 'This quiz is not currently available.')
        return redirect('quiz_detail', quiz_id=quiz_id)
    
    # Check if user can attempt this quiz
    user_attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz)
    if user_attempts.count() >= quiz.max_attempts:
        messages.error(request, 'You have reached the maximum number of attempts for this quiz.')
        return redirect('quiz_detail', quiz_id=quiz_id)
    
    # Check if it's a late submission
    is_late = quiz.is_late_submission_allowed()
    
    # Create new attempt
    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        status='in_progress',
        is_late_submission=is_late
    )
    
    if is_late:
        messages.warning(request, f'This is a late submission. A {quiz.late_submission_penalty}% penalty will be applied to your score.')
    
    return redirect('take_quiz', attempt_id=attempt.id)

@login_required
def take_quiz(request, attempt_id):
    """Take the quiz - display questions and handle submissions"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    # Check if attempt is still in progress
    if attempt.status != 'in_progress':
        return redirect('quiz_result', attempt_id=attempt_id)
    
    # Check time limit
    if attempt.time_remaining() <= 0:
        attempt.status = 'completed'
        attempt.finished_at = timezone.now()
        attempt.save()
        attempt.calculate_score()
        return redirect('quiz_result', attempt_id=attempt_id)
    
    # Get questions for this attempt (with randomization if enabled)
    questions = attempt.quiz.get_questions_for_attempt()
    
    if request.method == 'POST':
        # Process answers
        for question in questions:
            # Handle different question types
            if question.question_type in ['multiple_choice', 'true_false']:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    choice = get_object_or_404(Choice, id=choice_id, question=question)
                    Answer.objects.update_or_create(
                        attempt=attempt,
                        question=question,
                        defaults={'selected_choice': choice}
                    )
            
            elif question.question_type in ['short_answer', 'fill_blank', 'essay']:
                text_answer = request.POST.get(f'question_{question.id}_text', '').strip()
                if text_answer:
                    Answer.objects.update_or_create(
                        attempt=attempt,
                        question=question,
                        defaults={'text_answer': text_answer}
                    )
        
        # Complete the quiz
        attempt.status = 'completed'
        attempt.finished_at = timezone.now()
        
        # Calculate time taken
        time_diff = attempt.finished_at - attempt.started_at
        attempt.time_taken_minutes = int(time_diff.total_seconds() / 60)
        
        attempt.save()
        attempt.calculate_score()
        
        messages.success(request, f'Quiz completed! Your score: {attempt.score}/{attempt.total_marks}')
        return redirect('quiz_result', attempt_id=attempt_id)
    
    # Get choices for each question (with randomization if enabled)
    questions_with_choices = []
    for question in questions:
        question_data = {
            'question': question,
            'choices': question.get_choices_for_attempt() if question.question_type in ['multiple_choice', 'true_false'] else None
        }
        questions_with_choices.append(question_data)
    
    context = {
        'attempt': attempt,
        'questions_with_choices': questions_with_choices,
        'time_remaining': attempt.time_remaining(),
        'title': f'Taking: {attempt.quiz.title}'
    }
    return render(request, 'quizzes/take_quiz.html', context)

@login_required
def quiz_result(request, attempt_id):
    """Display quiz results"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    if attempt.status == 'in_progress':
        return redirect('take_quiz', attempt_id=attempt_id)
    
    answers = attempt.answers.all().select_related('question', 'selected_choice')
    
    # Separate answers by type for display
    auto_graded = answers.exclude(question__question_type__in=['essay'])
    manual_graded = answers.filter(question__question_type__in=['essay'])
    
    context = {
        'attempt': attempt,
        'answers': answers,
        'auto_graded': auto_graded,
        'manual_graded': manual_graded,
        'title': f'Results: {attempt.quiz.title}'
    }
    return render(request, 'quizzes/quiz_result.html', context)

@login_required
def my_quizzes(request):
    """Show user's created quizzes (for instructors)"""
    user_quizzes = Quiz.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Add statistics for each quiz
    for quiz in user_quizzes:
        quiz.total_attempts = quiz.attempts.count()
        quiz.completed_attempts = quiz.attempts.filter(status='completed').count()
        quiz.pending_grading = quiz.attempts.filter(requires_manual_grading=True, manually_graded_by__isnull=True).count()
    
    context = {
        'quizzes': user_quizzes,
        'title': 'My Created Quizzes'
    }
    return render(request, 'quizzes/my_quizzes.html', context)

@login_required
def question_banks(request):
    """List question banks for instructors"""
    if not request.user.userprofile.role in ['instructor', 'admin']:
        messages.error(request, 'You do not have permission to access question banks.')
        return redirect('home')
    
    banks = QuestionBank.objects.filter(created_by=request.user).order_by('category', 'name')
    
    context = {
        'question_banks': banks,
        'title': 'Question Banks'
    }
    return render(request, 'quizzes/question_banks.html', context)
