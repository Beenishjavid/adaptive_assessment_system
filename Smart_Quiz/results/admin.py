from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import QuizAttempt, Answer

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'group', 'status', 'score', 'percentage', 'started_at', 'finished_at']
    list_filter = ['status', 'quiz', 'group', 'started_at']
    search_fields = ['user__username', 'quiz__title', 'group__name']
    ordering = ['-started_at']
    readonly_fields = ['percentage']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'quiz', 'group')
        }),
        ('Attempt Details', {
            'fields': ('attempt_number', 'status', 'score', 'total_marks', 'percentage')
        }),
        ('Timing', {
            'fields': ('started_at', 'finished_at', 'time_taken_minutes')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'quiz', 'group')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_choice', 'is_correct', 'answered_at']
    list_filter = ['is_correct', 'attempt__quiz', 'question__question_type']
    search_fields = ['attempt__user__username', 'question__question_text']
    ordering = ['attempt', 'question__order']
    
    fieldsets = (
        (None, {
            'fields': ('attempt', 'question', 'selected_choice')
        }),
        ('Grading', {
            'fields': ('is_correct', 'answered_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'attempt', 'attempt__user', 'attempt__quiz', 'question', 'selected_choice'
        )
