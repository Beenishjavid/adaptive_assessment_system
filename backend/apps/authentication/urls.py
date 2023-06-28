"""
Authentication URL patterns
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import api_views
from apps import simple_admin_api
from apps import advanced_admin_api

urlpatterns = [
    # API Authentication endpoints
    path('api/login/', api_views.login_api, name='api_login'),
    path('api/logout/', api_views.logout_api, name='api_logout'),
    path('api/refresh/', api_views.refresh_token_api, name='api_refresh'),
    
    # JWT Authentication endpoints
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='user_register'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('change-password/', views.PasswordChangeView.as_view(), name='change_password'),
    
    # Password reset endpoints (legacy)
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('verify-reset-token/', views.VerifyResetTokenView.as_view(), name='verify_reset_token'),
    
    # OTP-based password reset endpoints
    path('password-reset/send-otp/', views.send_password_reset_otp, name='send_password_reset_otp'),
    path('password-reset/verify-otp/', views.verify_password_reset_otp, name='verify_password_reset_otp'),
    path('password-reset/reset-with-otp/', views.reset_password_with_otp, name='reset_password_with_otp'),
    
    # Organization endpoints
    path('organizations/', views.OrganizationListView.as_view(), name='organization_list'),
    
    # User management endpoints
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/approve/', views.approve_user, name='approve_user'),
    path('users/<int:user_id>/suspend/', views.suspend_user, name='suspend_user'),
    path('users/stats/', views.user_stats, name='user_stats'),
]

# Simple Admin URL patterns (working implementation)
admin_urlpatterns = [
    path('users/', simple_admin_api.admin_get_users, name='admin_users'),
    path('users/create/', simple_admin_api.admin_create_user, name='admin_create_user'),
    path('users/<int:user_id>/', simple_admin_api.admin_update_user, name='admin_update_user'),
    path('users/<int:user_id>/delete/', simple_admin_api.admin_delete_user, name='admin_delete_user'),
    path('organizations/', simple_admin_api.admin_get_organizations, name='admin_organizations'),
    path('stats/', simple_admin_api.admin_get_stats, name='admin_stats'),
    path('system-overview/', simple_admin_api.admin_system_overview, name='admin_system_overview'),
    path('users/<int:user_id>/toggle-status/', simple_admin_api.admin_toggle_user_status, name='admin_toggle_user_status'),
    
    # Advanced Admin Analytics & System Settings
    path('analytics/quiz/', advanced_admin_api.get_quiz_analytics, name='admin_quiz_analytics'),
    path('analytics/user/', advanced_admin_api.get_user_analytics, name='admin_user_analytics'),
    path('analytics/organization/', advanced_admin_api.get_organization_analytics, name='admin_organization_analytics'),
    path('activity/recent/', advanced_admin_api.get_recent_activity, name='admin_recent_activity'),
    path('settings/system/', advanced_admin_api.get_system_settings, name='admin_system_settings'),
    path('settings/system/update/', advanced_admin_api.update_system_settings, name='admin_update_system_settings'),
    path('system/info/', advanced_admin_api.get_system_info, name='admin_system_info'),
    path('system/backup/', advanced_admin_api.create_backup, name='admin_system_backup'),
    path('system/cache/clear/', advanced_admin_api.clear_cache, name='admin_clear_cache'),
]
