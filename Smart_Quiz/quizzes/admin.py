from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from .models import Quiz, Question, Choice, Topic, Assignment, QuestionBank

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ['choice_text', 'is_correct', 'order']

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ['question_text', 'question_type', 'marks', 'order', 'blank_answer', 'case_sensitive', 'manual_grading']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_topic', 'quiz_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent_topic', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent_topic')

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_by', 'total_questions', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category', 'description']
    ordering = ['category', 'name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'group', 'topic', 'quiz_type', 'visibility', 'is_active', 'created_at']
    list_filter = ['quiz_type', 'visibility', 'is_active', 'created_at', 'topic']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    inlines = [QuestionInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'created_by')
        }),
        ('Organization', {
            'fields': ('group', 'topic', 'quiz_type', 'visibility')
        }),
        ('Quiz Settings', {
            'fields': ('duration_minutes', 'passing_score', 'max_attempts', 'allow_review', 'randomize_questions')
        }),
        ('Scheduling', {
            'fields': ('start_time', 'end_time')
        }),
        ('Question Banks', {
            'fields': ('question_banks',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    filter_horizontal = ['question_banks']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by', 'group', 'topic')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'group', 'assigned_by', 'due_date', 'is_mandatory', 'assigned_at']
    list_filter = ['is_mandatory', 'assigned_at', 'due_date']
    search_fields = ['quiz__title', 'group__name', 'instructions']
    ordering = ['-assigned_at']
    
    fields = ['quiz', 'group', 'assigned_by', 'due_date', 'is_mandatory', 'max_attempts_override', 'instructions']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz', 'group', 'assigned_by')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text_short', 'quiz', 'question_bank', 'question_type', 'marks', 'order']
    list_filter = ['question_type', 'quiz', 'question_bank']
    search_fields = ['question_text']
    ordering = ['quiz', 'order']
    inlines = [ChoiceInline]
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = "Question Text"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz', 'question_bank')

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text_short', 'question', 'is_correct', 'order']
    list_filter = ['is_correct', 'question__quiz', 'question__question_type']
    search_fields = ['choice_text', 'question__question_text']
    ordering = ['question', 'order']
    
    def choice_text_short(self, obj):
        return obj.choice_text[:30] + "..." if len(obj.choice_text) > 30 else obj.choice_text
    choice_text_short.short_description = "Choice Text"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question', 'question__quiz')
