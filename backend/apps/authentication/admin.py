"""
Authentication Admin Configuration
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'  # Specify which ForeignKey to use
    can_delete = False
    verbose_name_plural = 'Profile'
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role', 'get_status')
    list_filter = BaseUserAdmin.list_filter + ('profile__role', 'profile__status')
    
    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else 'N/A'
    get_role.short_description = 'Role'
    
    def get_status(self, obj):
        return obj.profile.status if hasattr(obj, 'profile') else 'N/A'
    get_status.short_description = 'Status'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'status', 'organization', 'created_at')
    list_filter = ('role', 'status', 'organization', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'organization')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'status')
        }),
        ('Personal Details', {
            'fields': ('phone', 'bio', 'date_of_birth', 'organization')
        }),
        ('Approval Information', {
            'fields': ('approved_by', 'approved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
