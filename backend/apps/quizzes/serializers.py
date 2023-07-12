"""
Quiz Serializers - Convert models to JSON
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Quiz, Question, Choice, Topic


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topic model"""
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'parent_topic', 'is_active', 'created_at']


class ChoiceSerializer(serializers.ModelSerializer):
    """Serializer for Choice model"""
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model"""
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'marks', 'order', 'choices', 'created_at']


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model"""
    created_by = UserSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    total_questions = serializers.SerializerMethodField()
    total_marks = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'created_by', 'topic', 'quiz_type',
            'visibility', 'duration_minutes', 'passing_score', 'is_active',
            'max_attempts', 'allow_review', 'randomize_questions', 'start_time',
            'end_time', 'created_at', 'updated_at', 'questions', 'total_questions',
            'total_marks'
        ]
    
    def get_total_questions(self, obj):
        """Get total number of questions in the quiz"""
        return obj.questions.count()
    
    def get_total_marks(self, obj):
        """Get total marks for the quiz"""
        return sum(question.marks for question in obj.questions.all())


class QuizListSerializer(serializers.ModelSerializer):
    """Simplified serializer for quiz list view"""
    created_by = UserSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)
    total_questions = serializers.SerializerMethodField()
    total_marks = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'created_by', 'topic', 'quiz_type',
            'visibility', 'duration_minutes', 'passing_score', 'is_active',
            'max_attempts', 'start_time', 'end_time', 'created_at',
            'total_questions', 'total_marks'
        ]
    
    def get_total_questions(self, obj):
        """Get total number of questions in the quiz"""
        return obj.questions.count()
    
    def get_total_marks(self, obj):
        """Get total marks for the quiz"""
        return sum(question.marks for question in obj.questions.all())
