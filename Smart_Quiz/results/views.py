from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from .models import QuizAttempt, Answer

@login_required
def my_results(request):
    """Show user's quiz results"""
    attempts = QuizAttempt.objects.filter(user=request.user).order_by('-started_at')
    context = {
        'attempts': attempts,
        'title': 'My Quiz Results'
    }
    return render(request, 'results/my_results.html', context)

@login_required
def result_detail(request, attempt_id):
    """Show detailed result of a quiz attempt"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    
    # Check if user owns this attempt or is the quiz creator
    if attempt.user != request.user and attempt.quiz.created_by != request.user:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You don't have permission to view this result.")
    
    answers = Answer.objects.filter(attempt=attempt).select_related('question', 'selected_choice')
    
    context = {
        'attempt': attempt,
        'answers': answers,
        'title': f'Result: {attempt.quiz.title}'
    }
    return render(request, 'results/result_detail.html', context)

@login_required
def quiz_results(request, quiz_id):
    """Show all results for a quiz (for instructors)"""
    from quizzes.models import Quiz
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is the quiz creator
    if quiz.created_by != request.user:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You don't have permission to view these results.")
    
    attempts = QuizAttempt.objects.filter(quiz=quiz, status='completed').order_by('-finished_at')
    
    # Calculate analytics
    total_attempts = attempts.count()
    avg_score = attempts.aggregate(avg=Avg('percentage'))['avg'] or 0
    pass_rate = attempts.filter(percentage__gte=quiz.passing_score).count()
    pass_percentage = (pass_rate / total_attempts * 100) if total_attempts > 0 else 0
    
    context = {
        'quiz': quiz,
        'attempts': attempts,
        'total_attempts': total_attempts,
        'avg_score': round(avg_score, 1),
        'pass_rate': pass_rate,
        'pass_percentage': round(pass_percentage, 1),
        'title': f'Results: {quiz.title}'
    }
    return render(request, 'results/quiz_results.html', context)
