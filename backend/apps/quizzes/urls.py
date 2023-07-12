"""
Quiz URLs
"""
from django.urls import path
from . import views
from . import working_api_views
from . import quiz_management_views
from . import admin_views

app_name = 'quizzes'

urlpatterns = [
    # Working API endpoints that fetch real data
    path('api/dashboard/stats/', working_api_views.get_dashboard_stats, name='working_dashboard_stats'),
    path('api/quizzes/all/', working_api_views.get_all_quizzes, name='working_all_quizzes'),
    path('api/quizzes/<int:quiz_id>/', working_api_views.get_quiz_details, name='working_quiz_details'),
    path('api/user/profile/', working_api_views.get_user_profile, name='working_user_profile'),
    path('api/auth/login/', working_api_views.login_view, name='working_login'),
    
    # Quiz Management API endpoints
    path('api/quiz/create/', quiz_management_views.create_quiz, name='create_quiz'),
    path('api/quiz/my-quizzes/', quiz_management_views.get_my_quizzes, name='my_quizzes'),
    path('api/quiz/<int:quiz_id>/update/', quiz_management_views.update_quiz, name='update_quiz'),
    path('api/quiz/<int:quiz_id>/delete/', quiz_management_views.delete_quiz, name='delete_quiz'),
    path('api/quiz/<int:quiz_id>/preview/', quiz_management_views.get_quiz_preview, name='quiz_preview'),
    path('api/quiz/<int:quiz_id>/edit/', quiz_management_views.get_quiz_for_editing, name='quiz_edit'),
    path('api/quiz/<int:quiz_id>/results/', quiz_management_views.get_quiz_results_analytics, name='quiz_results'),
    
    # Quiz Taking API endpoints
    path('api/quiz/<int:quiz_id>/start/', quiz_management_views.start_quiz_attempt, name='start_quiz'),
    path('api/attempt/<int:attempt_id>/quiz/', quiz_management_views.get_quiz_for_attempt, name='get_quiz_for_attempt'),
    path('api/attempt/<int:attempt_id>/answer/', quiz_management_views.submit_quiz_answer, name='submit_answer'),
    path('api/attempt/<int:attempt_id>/submit/', quiz_management_views.submit_quiz, name='submit_quiz'),
    path('api/attempt/<int:attempt_id>/result/', quiz_management_views.get_quiz_result, name='quiz_result'),
    path('api/user/attempts/', quiz_management_views.get_user_quiz_attempts, name='user_attempts'),
    path('api/my-results/', quiz_management_views.get_my_results, name='my_results'),
    path('api/instructor/stats/', quiz_management_views.get_instructor_stats, name='instructor_stats'),
    path('api/instructor/quiz-attempts/', quiz_management_views.get_instructor_quiz_attempts, name='instructor_quiz_attempts'),
    
    # Admin endpoints
    path('admin/quiz-stats/', admin_views.get_quiz_stats, name='admin_quiz_stats'),
    path('admin/recent-activity/', admin_views.get_recent_activity, name='admin_recent_activity'),
    
    # Original endpoints (keeping for compatibility)
    path('', views.quiz_list, name='quiz-list'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz-detail'),
    path('<int:quiz_id>/questions/', views.quiz_questions, name='quiz-questions'),
    path('topics/', views.topics_list, name='topics-list'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]
