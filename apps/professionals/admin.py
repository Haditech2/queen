from django.contrib import admin
from .models import Professional

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'state', 'city', 'phone', 'consultation_mode', 'is_verified', 'verification_date')
    list_filter = ('is_verified', 'category', 'state', 'consultation_mode')
    search_fields = ('name', 'city', 'services_offered', 'license_number')
    actions = ['verify_selected_professionals']

    def verify_selected_professionals(self, request, queryset):
        queryset.update(is_verified=True)
    verify_selected_professionals.short_description = "Verify and publish selected healthcare providers"
