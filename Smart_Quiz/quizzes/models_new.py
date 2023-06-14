from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import random

class Topic(models.Model):
    """Hierarchical topic categorization for quizzes"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent_topic = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subtopics'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.parent_topic:
            return f"{self.parent_topic.name} > {self.name}"
        return self.name
    
    def get_full_path(self):
        """Get the full hierarchical path of the topic"""
        path = [self.name]
        current = self.parent_topic
        while current:
            path.append(current.name)
            current = current.parent_topic
        return " > ".join(reversed(path))
    
    def get_all_subtopics(self):
        """Get all subtopics recursively"""
        subtopics = list(self.subtopics.filter(is_active=True))
        for subtopic in list(subtopics):
            subtopics.extend(subtopic.get_all_subtopics())
        return subtopics
    
    def quiz_count(self):
        """Get count of quizzes in this topic and all subtopics"""
        topic_ids = [self.id] + [t.id for t in self.get_all_subtopics()]
        return Quiz.objects.filter(topic_id__in=topic_ids, is_active=True).count()
    
    class Meta:
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        ordering = ['name']

class QuestionBank(models.Model):
    """Reusable question repository with categorization"""
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_banks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def total_questions(self):
        return self.bank_questions.count()
    
    class Meta:
        ordering = ['category', 'name']

class Quiz(models.Model):
    """Enhanced Quiz model with group and topic support"""
    
    QUIZ_TYPES = [
        ('assessment', 'Assessment'),
        ('practice', 'Practice'),
        ('self_study', 'Self Study'),
        ('group_study', 'Group Study'),
    ]
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('group', 'Group'),
        ('public', 'Public'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    
    # Group and topic relationships
    group = models.ForeignKey(
        'groups.Group', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='quizzes',
        help_text="Link to group (NULL for no-group quizzes)"
    )
    topic = models.ForeignKey(
        Topic, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='quizzes',
        help_text="Topic categorization"
    )
    
    # Quiz configuration
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES, default='assessment')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    duration_minutes = models.IntegerField(default=60)
    passing_score = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    max_attempts = models.IntegerField(default=1)
    allow_review = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=False)
    
    # Scheduling
    start_time = models.DateTimeField(null=True, blank=True, help_text="Scheduled start time")
    end_time = models.DateTimeField(null=True, blank=True, help_text="Scheduled end time")
    
    # Late submission handling
    allow_late_submission = models.BooleanField(default=False)
    late_submission_penalty = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)], 
        help_text="Percentage penalty for late submissions"
    )
    grace_period_minutes = models.IntegerField(default=0, help_text="Grace period in minutes after end time")
    
    # Randomization features
    randomize_choices = models.BooleanField(default=False, help_text="Randomize answer choice order")
    questions_per_attempt = models.IntegerField(
        null=True, 
        blank=True, 
        help_text="Limit number of questions per attempt (random selection)"
    )
    
    # Question bank integration
    question_banks = models.ManyToManyField(QuestionBank, blank=True, help_text="Select question banks to include")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def total_marks(self):
        return sum(question.marks for question in self.questions.all())
    
    def total_questions(self):
        base_questions = self.questions.count()
        bank_questions = sum(bank.total_questions() for bank in self.question_banks.all())
        return base_questions + bank_questions
    
    def is_available(self):
        """Check if quiz is currently available"""
        now = timezone.now()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time and not self.allow_late_submission:
            return False
        return self.is_active
    
    def is_late_submission_allowed(self):
        """Check if late submission is currently allowed"""
        if not self.allow_late_submission or not self.end_time:
            return False
        now = timezone.now()
        grace_end = self.end_time + timezone.timedelta(minutes=self.grace_period_minutes)
        return self.end_time < now <= grace_end
    
    def get_questions_for_attempt(self):
        """Get questions for a new attempt (with randomization if enabled)"""
        # Get quiz-specific questions
        quiz_questions = list(self.questions.all())
        
        # Get questions from question banks
        bank_questions = []
        for bank in self.question_banks.all():
            bank_questions.extend(list(bank.bank_questions.all()))
        
        # Combine all questions
        all_questions = quiz_questions + bank_questions
        
        # Apply randomization
        if self.randomize_questions:
            random.shuffle(all_questions)
        
        # Limit number of questions if specified
        if self.questions_per_attempt and len(all_questions) > self.questions_per_attempt:
            all_questions = all_questions[:self.questions_per_attempt]
        
        return all_questions
    
    def can_user_access(self, user):
        """Check if user can access this quiz"""
        if not self.is_active:
            return False, "Quiz is not active"
        
        # Check visibility
        if self.visibility == 'private':
            # Only creator can access
            return user == self.created_by, "Quiz is private"
        
        elif self.visibility == 'group':
            # Check if user is member of the group
            if not self.group:
                return False, "Quiz group not found"
            
            is_member = self.group.memberships.filter(
                user=user, 
                is_active=True
            ).exists()
            return is_member, "User must be a group member" if not is_member else "Access granted"
        
        elif self.visibility == 'public':
            # Anyone can access public quizzes
            return True, "Public quiz access granted"
        
        return False, "Access denied"
    
    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

class Assignment(models.Model):
    """Quiz assignment system for groups"""
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='assignments')
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name='quiz_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_quizzes')
    
    due_date = models.DateTimeField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=True)
    max_attempts_override = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Override quiz max attempts for this assignment"
    )
    instructions = models.TextField(blank=True, help_text="Special instructions for this assignment")
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quiz.title} assigned to {self.group.name}"
    
    def is_overdue(self):
        """Check if assignment is overdue"""
        if not self.due_date:
            return False
        return timezone.now() > self.due_date
    
    def days_until_due(self):
        """Get days until due date"""
        if not self.due_date:
            return None
        delta = self.due_date - timezone.now()
        return delta.days
    
    def get_max_attempts(self):
        """Get max attempts for this assignment (override or quiz default)"""
        return self.max_attempts_override or self.quiz.max_attempts
    
    def get_completion_stats(self):
        """Get completion statistics for this assignment"""
        from results.models import QuizAttempt
        
        total_members = self.group.member_count()
        completed_attempts = QuizAttempt.objects.filter(
            quiz=self.quiz,
            user__group_memberships__group=self.group,
            user__group_memberships__is_active=True,
            status='completed'
        ).values('user').distinct().count()
        
        return {
            'total_members': total_members,
            'completed_count': completed_attempts,
            'completion_rate': (completed_attempts / total_members * 100) if total_members > 0 else 0,
            'pending_count': total_members - completed_attempts
        }
    
    class Meta:
        unique_together = ('quiz', 'group')
        verbose_name = "Quiz Assignment"
        verbose_name_plural = "Quiz Assignments"
        ordering = ['-assigned_at']

class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('fill_blank', 'Fill in the Blank'),
        ('essay', 'Essay Question'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    question_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='bank_questions', null=True, blank=True)
    
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    marks = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    
    # Fill in the blank specific fields
    blank_answer = models.TextField(blank=True, help_text="Correct answer for fill-in-the-blank questions")
    case_sensitive = models.BooleanField(default=False, help_text="Whether fill-in-the-blank answers are case sensitive")
    
    # Essay question specific fields
    manual_grading = models.BooleanField(default=False, help_text="Requires manual grading")
    essay_max_words = models.IntegerField(null=True, blank=True, help_text="Maximum word count for essay questions")
    grading_rubric = models.TextField(blank=True, help_text="Grading criteria for essay questions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        source = self.quiz.title if self.quiz else self.question_bank.name
        return f"{source} - {self.question_text[:50]}..."
    
    def get_choices_for_attempt(self):
        """Get choices with randomization if enabled"""
        choices = list(self.choices.all())
        
        # Check if the quiz (or question bank's quiz usage) has randomization enabled
        should_randomize = False
        if self.quiz and self.quiz.randomize_choices:
            should_randomize = True
        elif self.question_bank:
            # Check if any quiz using this question bank has randomization enabled
            for quiz in Quiz.objects.filter(question_banks=self.question_bank):
                if quiz.randomize_choices:
                    should_randomize = True
                    break
        
        if should_randomize:
            random.shuffle(choices)
        
        return choices
    
    class Meta:
        ordering = ['order', 'id']

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.choice_text[:50]}..."
    
    class Meta:
        ordering = ['order', 'id']
