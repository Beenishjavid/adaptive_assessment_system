from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class QuizAttempt(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('submitted_late', 'Submitted Late'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey('quizzes.Quiz', on_delete=models.CASCADE, related_name='attempts')
    
    # Group context for tracking group quiz attempts
    group = models.ForeignKey(
        'groups.Group', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='quiz_attempts',
        help_text="Group context if quiz was taken as part of group assignment"
    )
    assignment = models.ForeignKey(
        'quizzes.Assignment', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='attempts',
        help_text="Link to quiz assignment if applicable"
    )
    
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    # Scoring
    score = models.IntegerField(null=True, blank=True)
    total_marks = models.IntegerField(default=0)
    percentage = models.FloatField(null=True, blank=True)
    time_taken_minutes = models.IntegerField(null=True, blank=True)
    
    # Late submission handling
    is_late_submission = models.BooleanField(default=False)
    late_penalty_applied = models.IntegerField(default=0, help_text="Percentage penalty applied for late submission")
    original_score = models.IntegerField(null=True, blank=True, help_text="Score before late penalty")
    
    # Manual grading tracking
    requires_manual_grading = models.BooleanField(default=False)
    manually_graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_attempts')
    graded_at = models.DateTimeField(null=True, blank=True)
    grading_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.status})"
    
    def calculate_score(self):
        """Calculate automatic score and handle manual grading requirements"""
        auto_gradable_answers = self.answers.exclude(question__question_type__in=['essay'])
        correct_auto_answers = auto_gradable_answers.filter(is_correct=True)
        
        auto_score = sum(answer.question.marks for answer in correct_auto_answers)
        
        # Check if manual grading is required
        essay_questions = self.answers.filter(question__question_type='essay')
        if essay_questions.exists():
            self.requires_manual_grading = True
        
        # Add manually graded scores
        manual_score = sum(answer.manual_score or 0 for answer in self.answers.filter(question__question_type='essay'))
        
        total_score = auto_score + manual_score
        
        # Apply late submission penalty if applicable
        if self.is_late_submission and hasattr(self.quiz, 'late_submission_penalty') and self.quiz.late_submission_penalty > 0:
            self.original_score = total_score
            penalty = (self.quiz.late_submission_penalty / 100) * total_score
            total_score = max(0, total_score - penalty)
            self.late_penalty_applied = getattr(self.quiz, 'late_submission_penalty', 0)
        
        self.score = total_score
        self.total_marks = self.quiz.total_marks()
        
        if self.total_marks > 0:
            self.percentage = (self.score / self.total_marks) * 100
        else:
            self.percentage = 0
        
        self.save()
        return self.score
    
    def is_passed(self):
        if self.percentage is not None:
            return self.percentage >= self.quiz.passing_score
        return False
    
    def time_remaining(self):
        if self.status == 'completed':
            return 0
        elapsed = timezone.now() - self.started_at
        elapsed_minutes = elapsed.total_seconds() / 60
        remaining = self.quiz.duration_minutes - elapsed_minutes
        return max(0, remaining)
    
    def grading_status(self):
        """Return human-readable grading status"""
        if not self.requires_manual_grading:
            return "Auto-graded"
        elif self.manually_graded_by:
            return f"Manually graded by {self.manually_graded_by.username}"
        else:
            return "Pending manual grading"
    
    def get_group_rank(self):
        """Get user's rank within the group for this quiz"""
        if not self.group:
            return None
        
        # Get all completed attempts for this quiz within the group
        group_attempts = QuizAttempt.objects.filter(
            quiz=self.quiz,
            group=self.group,
            status='completed'
        ).order_by('-percentage', 'finished_at')
        
        for index, attempt in enumerate(group_attempts, 1):
            if attempt.id == self.id:
                return index
        
        return None
    
    def get_assignment_context(self):
        """Get assignment context information"""
        if not self.assignment:
            return None
        
        return {
            'due_date': self.assignment.due_date,
            'is_overdue': self.assignment.is_overdue(),
            'is_mandatory': self.assignment.is_mandatory,
            'instructions': self.assignment.instructions,
            'days_until_due': self.assignment.days_until_due()
        }
    
    class Meta:
        verbose_name = "Quiz Attempt"
        verbose_name_plural = "Quiz Attempts"
        ordering = ['-started_at']

class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('quizzes.Question', on_delete=models.CASCADE)
    
    # Multiple choice answers
    selected_choice = models.ForeignKey('quizzes.Choice', on_delete=models.CASCADE, null=True, blank=True)
    
    # Text-based answers (short answer, fill-in-blank, essay)
    text_answer = models.TextField(blank=True)
    
    # Manual grading fields
    manual_score = models.IntegerField(null=True, blank=True, help_text="Manually assigned score")
    grader_comments = models.TextField(blank=True)
    
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.question_text[:30]}..."
    
    def check_answer(self):
        """Check if answer is correct based on question type"""
        if self.question.question_type in ['multiple_choice', 'true_false']:
            if self.selected_choice:
                return self.selected_choice.is_correct
        elif self.question.question_type == 'fill_blank':
            if self.text_answer and self.question.blank_answer:
                if self.question.case_sensitive:
                    return self.text_answer.strip() == self.question.blank_answer.strip()
                else:
                    return self.text_answer.strip().lower() == self.question.blank_answer.strip().lower()
        elif self.question.question_type == 'short_answer':
            # For short answers, we might need keyword matching or manual grading
            # For now, return False to require manual grading
            return False
        elif self.question.question_type == 'essay':
            # Essays always require manual grading
            return False
        
        return False
    
    def save(self, *args, **kwargs):
        # Auto-check correctness for applicable question types
        if self.question.question_type not in ['essay', 'short_answer']:
            self.is_correct = self.check_answer()
        
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ('attempt', 'question')
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
