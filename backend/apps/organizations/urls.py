"""
Organizations URL patterns
"""
from django.urls import path
from . import admin_views, views

urlpatterns = [
    # Public organization endpoints (for registration)
    path('', views.OrganizationListView.as_view(), name='organization_list'),
    
    # Admin organization management endpoints
    path('admin/organizations/', admin_views.get_all_organizations, name='admin_organizations'),
    path('admin/organizations/create/', admin_views.create_organization, name='admin_create_organization'),
    path('admin/organizations/<int:org_id>/', admin_views.update_organization, name='admin_update_organization'),
    path('admin/organizations/<int:org_id>/delete/', admin_views.delete_organization, name='admin_delete_organization'),
    path('admin/organization-stats/', admin_views.get_organization_stats, name='admin_organization_stats'),
]
