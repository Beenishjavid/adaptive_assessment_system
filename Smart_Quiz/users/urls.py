from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('instructor-dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Admin management URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:profile_id>/', views.approve_user, name='approve_user'),
    path('reject/<int:profile_id>/', views.reject_user, name='reject_user'),
    path('profile/<int:profile_id>/', views.view_profile_detail, name='view_profile_detail'),
    path('edit/<int:profile_id>/', views.edit_user, name='edit_user'),
    path('delete/<int:profile_id>/', views.delete_user, name='delete_user'),
    path('export/', views.export_users, name='export_users'),
]
