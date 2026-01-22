from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.accounts.models import User, Profile


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('email', 'username', 'subscription_tier', 'is_active', 'date_joined')
    list_filter = ('subscription_tier', 'is_active', 'date_joined')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username',)}),
        ('Subscription', {'fields': ('subscription_tier', 'requests_per_hour', 'tokens_per_hour')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__email', 'github_username')
