from django.contrib import admin
from django.utils.html import format_html
from .models import Group, Membership, Invitation

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    fields = ('user', 'role_in_group', 'is_active', 'joined_at')
    readonly_fields = ('joined_at',)

class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 0
    fields = ('email', 'invited_user', 'status', 'expires_at', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_type', 'created_by', 'is_active', 'member_count_display', 'join_code', 'created_at')
    list_filter = ('group_type', 'is_active', 'created_at', 'created_by')
    search_fields = ('name', 'description', 'join_code')
    readonly_fields = ('join_code', 'created_at', 'updated_at')
    inlines = [MembershipInline, InvitationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'group_type', 'created_by')
        }),
        ('Settings', {
            'fields': ('is_active', 'max_members', 'auto_approve_members')
        }),
        ('Access', {
            'fields': ('join_code',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new group
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def member_count_display(self, obj):
        return obj.member_count()
    member_count_display.short_description = 'Members'

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role_in_group', 'is_active', 'joined_at')
    list_filter = ('role_in_group', 'is_active', 'joined_at', 'group__group_type')
    search_fields = ('user__username', 'group__name')
    readonly_fields = ('joined_at',)

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'invited_user', 'group', 'status', 'expires_at', 'created_at')
    list_filter = ('status', 'created_at', 'expires_at')
    search_fields = ('email', 'group__name', 'invited_user__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Invitation Details', {
            'fields': ('group', 'email', 'invited_user', 'invited_by')
        }),
        ('Status', {
            'fields': ('status', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'used_at'),
            'classes': ('collapse',)
        }),
    )
