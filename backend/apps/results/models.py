"""
Results Models
"""
from django.db import models
from django.contrib.auth.models import User
from apps.quizzes.models import Quiz, Question, Choice


class QuizAttempt(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    group = models.ForeignKey('groups.Group', on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.IntegerField(null=True, blank=True)
    total_marks = models.IntegerField(default=0)
    percentage = models.FloatField(null=True, blank=True)
    time_taken_minutes = models.IntegerField(null=True, blank=True)
    attempt_number = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'results_quizattempt'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} (Attempt #{self.attempt_number})"


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'results_answer'
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"Answer for {self.question.question_text[:50]}..."
