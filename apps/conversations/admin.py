from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('role', 'content_preview', 'risk_level', 'is_reported', 'report_reason', 'created_at')
    fields = ('role', 'content_preview', 'risk_level', 'is_reported', 'report_reason', 'created_at')
    can_delete = False

    def content_preview(self, obj):
        # Privacy preservation: mask non-reported messages to prevent unauthorized reading of sensitive health notes
        if obj.is_reported or obj.risk_level in ('HIGH', 'IMMINENT'):
            return obj.content[:150]
        return "[Protected Private Chat Content]"
    content_preview.short_description = "Message Content (Privacy Guarded)"

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'language', 'created_at', 'updated_at', 'is_archived')
    list_filter = ('language', 'is_archived', 'created_at')
    search_fields = ('title', 'user__email')
    inlines = [MessageInline]
    readonly_fields = ('id', 'user', 'created_at', 'updated_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'risk_level', 'is_reported', 'created_at')
    list_filter = ('role', 'risk_level', 'is_reported')
    search_fields = ('report_reason',)
    readonly_fields = ('id', 'conversation', 'role', 'content_display', 'risk_level', 'is_reported', 'report_reason', 'created_at')

    def content_display(self, obj):
        if obj.is_reported or obj.risk_level in ('HIGH', 'IMMINENT'):
            return obj.content
        return "[Protected by Privacy Controls: Visible only on explicit user report or safety trigger]"
    content_display.short_description = "Content"
