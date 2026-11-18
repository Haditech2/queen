from django.contrib import admin
from .models import CrisisResource, MentalHealthResource

@admin.register(CrisisResource)
class CrisisResourceAdmin(admin.ModelAdmin):
    list_display = ('organization', 'location_state', 'phone', 'service_type', 'is_24_7', 'is_emergency_priority', 'is_verified', 'verification_date')
    list_filter = ('is_verified', 'is_emergency_priority', 'is_24_7', 'location_state', 'service_type')
    search_fields = ('organization', 'phone', 'description', 'location_state')
    actions = ['mark_as_verified']

    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
    mark_as_verified.short_description = "Mark selected resources as Verified"

@admin.register(MentalHealthResource)
class MentalHealthResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'location_state', 'resource_type', 'is_verified')
    list_filter = ('resource_type', 'is_verified', 'location_state')
    search_fields = ('title', 'organization', 'services_offered')
