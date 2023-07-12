"""
Quizzes Models - Matching the existing SmartQuizDB schema
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Quiz(models.Model):
    """Quiz model matching the existing Quiz table"""
    quiz_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    time_limit = models.IntegerField(help_text="Time limit in minutes")
    total_marks = models.IntegerField()
    pass_percentage = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes', db_column='created_by')
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'Quiz'
        managed = False  # Don't let Django manage this table

    def __str__(self):
        return self.title


class Question(models.Model):
    """Question model matching the existing Question table"""
    question_id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', db_column='quiz_id')
    question_text = models.TextField()
    question_type = models.CharField(max_length=50)
    marks = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Question'
        managed = False

    def __str__(self):
        return f"Q{self.question_id}: {self.question_text[:50]}..."


class Option(models.Model):
    """Option model matching the existing Option table"""
    option_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', db_column='question_id')
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'Option'
        managed = False

    def __str__(self):
        return f"{self.option_text[:30]}..."


class QuizAttempt(models.Model):
    """QuizAttempt model matching the existing QuizAttempt table"""
    attempt_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts', db_column='user_id')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts', db_column='quiz_id')
    score = models.IntegerField()
    total_questions = models.IntegerField()
    time_taken = models.IntegerField(help_text="Time taken in minutes")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_passed = models.BooleanField()

    class Meta:
        db_table = 'QuizAttempt'
        managed = False

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"


class UserAnswer(models.Model):
    """UserAnswer model matching the existing UserAnswer table"""
    answer_id = models.AutoField(primary_key=True)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers', db_column='attempt_id')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, db_column='question_id')
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True, db_column='selected_option_id')
    answer_text = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField()
    marks_obtained = models.IntegerField()

    class Meta:
        db_table = 'UserAnswer'
        managed = False

    def __str__(self):
        return f"{self.attempt.user.username} - Q{self.question.question_id}"


# Keep the existing Django-managed models for new features
class Topic(models.Model):
    """Quiz topics for categorization"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent_topic = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'quizzes_topic'

    def __str__(self):
        return self.name
