from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('attempt/<int:attempt_id>/', views.take_quiz, name='take_quiz'),
    path('result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    path('my-quizzes/', views.my_quizzes, name='my_quizzes'),
    path('question-banks/', views.question_banks, name='question_banks'),
]
