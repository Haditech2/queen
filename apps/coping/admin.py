from django.contrib import admin
from .models import CopingTool

@admin.register(CopingTool)
class CopingToolAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'duration_minutes', 'is_interactive', 'is_active', 'order')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'short_description', 'overview')
    prepopulated_fields = {'slug': ('title',)}
