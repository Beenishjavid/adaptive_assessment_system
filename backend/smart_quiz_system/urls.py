"""
Smart Quiz System URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import debug_views
from apps import admin_api
from apps.authentication.urls import admin_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/organizations/', include('apps.organizations.urls')),
    path('api/groups/', include('apps.groups.urls')),
    path('api/quizzes/', include('apps.quizzes.urls')),
    path('api/results/', include('apps.results.urls')),
    path('api/proctoring/', include('apps.proctoring.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    
    # Admin API endpoints
    path('api/admin/', include(admin_urlpatterns)),
    
    path('debug/users/', debug_views.debug_users, name='debug_users'),  # Debug endpoint
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "Smart Quiz System Administration"
admin.site.site_title = "Smart Quiz Admin"
admin.site.index_title = "Welcome to Smart Quiz Administration"
