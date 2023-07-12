"""
Quizzes Models - Match existing database schema
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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


class Quiz(models.Model):
    """Enhanced Quiz model with full group integration"""
    QUIZ_TYPE_CHOICES = [
        ('assessment', 'Formal Assessment'),     # Faculty assessments for grading
        ('practice', 'Practice Quiz'),          # General practice quizzes
        ('self_study', 'Self Assessment'),      # Individual student self-evaluation
        ('group_study', 'Group Study'),         # Collaborative learning within groups
    ]
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),                 # Only creator can see
        ('group', 'Group Only'),               # Only group members can access
        ('public', 'Public'),                  # Anyone can find and take
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    
    # Group integration
    group = models.ForeignKey('groups.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    
    # Quiz configuration
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPE_CHOICES, default='assessment')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    duration_minutes = models.IntegerField(default=60, help_text="Quiz duration in minutes")
    passing_score = models.IntegerField(default=60, help_text="Minimum score to pass (%)")
    is_active = models.BooleanField(default=True)
    max_attempts = models.IntegerField(default=1, help_text="Maximum attempts allowed")
    allow_review = models.BooleanField(default=True, help_text="Allow students to review after completion")
    randomize_questions = models.BooleanField(default=False, help_text="Randomize question order")
    
    # Scheduling
    start_time = models.DateTimeField(null=True, blank=True, help_text="When quiz becomes available")
    end_time = models.DateTimeField(null=True, blank=True, help_text="When quiz expires")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quizzes_quiz'

    def __str__(self):
        group_info = f" ({self.group.name})" if self.group else ""
        return f"{self.title}{group_info}"

    def can_user_access(self, user):
        """Check if a user can access this quiz"""
        # Creator can always access
        if self.created_by == user:
            return True, "Creator access"
        
        # Check if quiz is active
        if not self.is_active:
            return False, "Quiz is inactive"
        
        # Check scheduling
        now = timezone.now()
        if self.start_time and now < self.start_time:
            return False, "Quiz not yet available"
        if self.end_time and now > self.end_time:
            return False, "Quiz has expired"
        
        # Check visibility and group membership
        if self.visibility == 'private':
            return False, "Private quiz"
        elif self.visibility == 'group':
            if not self.group:
                return False, "Group quiz without group"
            if not self.group.memberships.filter(user=user, is_active=True).exists():
                return False, "Not a group member"
        # Public quizzes are accessible to all
        
        return True, "Access granted"

    def get_user_attempts(self, user):
        """Get user's attempts for this quiz"""
        return self.attempts.filter(user=user).order_by('-started_at')

    def can_user_attempt(self, user):
        """Check if user can start a new attempt"""
        can_access, reason = self.can_user_access(user)
        if not can_access:
            return False, reason
        
        # Check attempt limit
        attempts_count = self.get_user_attempts(user).count()
        if attempts_count >= self.max_attempts:
            return False, f"Maximum attempts ({self.max_attempts}) reached"
        
        # Check for ongoing attempt
        ongoing_attempt = self.get_user_attempts(user).filter(status='in_progress').first()
        if ongoing_attempt:
            return False, "You have an ongoing attempt"
        
        return True, "Can start new attempt"

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def total_marks(self):
        return sum(q.marks for q in self.questions.all())

    @property
    def attempt_count(self):
        return self.attempts.count()

    @property
    def completion_count(self):
        return self.attempts.filter(status='completed').count()

    def get_analytics(self):
        """Get quiz analytics data"""
        attempts = self.attempts.filter(status='completed')
        if not attempts.exists():
            return {
                'total_attempts': 0,
                'completion_rate': 0,
                'average_score': 0,
                'pass_rate': 0
            }
        
        total_attempts = self.attempts.count()
        completed_attempts = attempts.count()
        
        scores = [attempt.percentage for attempt in attempts if attempt.percentage is not None]
        passed_attempts = [score for score in scores if score >= self.passing_score]
        
        return {
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts,
            'completion_rate': (completed_attempts / total_attempts * 100) if total_attempts > 0 else 0,
            'average_score': sum(scores) / len(scores) if scores else 0,
            'pass_rate': (len(passed_attempts) / len(scores) * 100) if scores else 0
        }


class Question(models.Model):
    """Question model matching database schema"""
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='multiple_choice')
    marks = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'quizzes_question'
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class Choice(models.Model):
    """Choice model matching database schema"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'quizzes_choice'
        ordering = ['order']

    def __str__(self):
        return f"{self.choice_text[:30]}..."
