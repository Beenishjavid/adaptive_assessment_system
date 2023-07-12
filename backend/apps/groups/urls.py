"""
Groups URL patterns - Enhanced group management system
"""
from django.urls import path
from . import views
from . import group_api_views

urlpatterns = [
    # Group CRUD operations
    path('', views.GroupListCreateView.as_view(), name='group-list-create'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group-detail'),
    
    # Enhanced group management
    path('by-type/', group_api_views.get_user_groups_by_type, name='groups-by-type'),
    path('discover/', group_api_views.discover_public_groups, name='discover-groups'),
    path('search-by-topic/', group_api_views.search_quizzes_by_topic, name='search-by-topic'),
    
    # Group listings (original)
    path('my-groups/', views.MyGroupsView.as_view(), name='my-groups'),
    path('public/', views.PublicGroupsView.as_view(), name='public-groups'),
    
    # Enhanced membership operations
    path('join/', group_api_views.join_group_enhanced, name='join-group-enhanced'),
    path('<int:group_id>/leave/', group_api_views.leave_group_enhanced, name='leave-group-enhanced'),
    path('<int:group_id>/quizzes/', group_api_views.get_group_quizzes, name='group-quizzes'),
    path('<int:group_id>/assign-quiz/', group_api_views.assign_quiz_to_group, name='assign-quiz'),
    path('<int:group_id>/analytics/', group_api_views.get_group_analytics, name='group-analytics'),
    
    # Legacy endpoints (keeping for compatibility)
    path('join-legacy/', views.join_group, name='join-group'),
    path('<int:group_id>/leave-legacy/', views.leave_group, name='leave-group'),
    path('<int:group_id>/add-member/', views.add_member, name='add-member'),
    path('<int:group_id>/remove-member/<int:user_id>/', views.remove_member, name='remove-member'),
    
    # Utility endpoints
    path('search/', views.search_groups, name='search-groups'),
    path('<int:group_id>/generate-join-code/', views.generate_join_code, name='generate-join-code'),
    path('available-users/', views.get_available_users, name='available-users'),
]
