from django.contrib import admin
from .models import ScreeningTool, ScreeningSession, ScreeningResponse

class ScreeningResponseInline(admin.TabularInline):
    model = ScreeningResponse
    extra = 0
    readonly_fields = ('question_index', 'question_text', 'selected_value', 'selected_label')
    can_delete = False

@admin.register(ScreeningTool)
class ScreeningToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'tool_type', 'is_active')
    list_filter = ('tool_type', 'is_active')

@admin.register(ScreeningSession)
class ScreeningSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tool', 'total_score', 'severity_label', 'completed_at')
    list_filter = ('tool', 'severity_label', 'completed_at')
    search_fields = ('user__email',)
    inlines = [ScreeningResponseInline]
    readonly_fields = ('user', 'tool', 'total_score', 'severity_label', 'interpretation', 'completed_at')
