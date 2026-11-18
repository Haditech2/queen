from django.contrib import admin
from .models import MoodCheckIn

@admin.register(MoodCheckIn)
class MoodCheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'mood', 'stress_level', 'sleep_quality', 'created_at')
    list_filter = ('mood', 'sleep_quality', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('user', 'mood', 'stress_level', 'sleep_quality', 'note_display', 'created_at')

    def note_display(self, obj):
        return "[Protected by Privacy Controls: Personal Reflection]"
    note_display.short_description = "Note"
