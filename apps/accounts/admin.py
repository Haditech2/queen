from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Cultural & Support Preferences'

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    inlines = [UserProfileInline]
    list_display = ('email', 'first_name', 'last_name', 'state_region', 'preferred_language', 'is_staff', 'is_verified')
    list_filter = ('is_staff', 'is_superuser', 'is_verified', 'preferred_language', 'state_region')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'age_range', 'gender', 'state_region')}),
        ('Cultural & Language Preferences', {'fields': ('preferred_language', 'preferred_communication_style')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Verification & Dates', {'fields': ('is_verified', 'verification_token', 'date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password', 'confirm_password', 'preferred_language'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'faith_preference', 'emergency_contact_name', 'allow_ai_personalization')
    search_fields = ('user__email', 'emergency_contact_name')
