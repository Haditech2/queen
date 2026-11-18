from django.contrib import admin
from .models import SafetyRule, SafetyEvent

@admin.register(SafetyRule)
class SafetyRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_type', 'risk_level', 'is_active', 'updated_at')
    list_filter = ('risk_level', 'rule_type', 'is_active')
    search_fields = ('name', 'patterns', 'custom_guidance')

@admin.register(SafetyEvent)
class SafetyEventAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'risk_level', 'category', 'user', 'location_state', 'matched_pattern_sanitized')
    list_filter = ('risk_level', 'category', 'location_state', 'timestamp')
    search_fields = ('user__email', 'matched_pattern_sanitized', 'intervention_taken')
    readonly_fields = ('timestamp', 'risk_level', 'category', 'matched_pattern_sanitized', 'intervention_taken', 'session_id', 'location_state')

    def has_add_permission(self, request):
        return False
