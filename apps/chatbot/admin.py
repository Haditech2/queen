from django.contrib import admin
from .models import AIProvider, AIModel

class AIModelInline(admin.TabularInline):
    model = AIModel
    extra = 1

@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider_type', 'base_url', 'is_active')
    list_filter = ('provider_type', 'is_active')
    inlines = [AIModelInline]

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'model_identifier', 'provider', 'is_default', 'is_active')
    list_filter = ('provider', 'is_default', 'is_active')
    search_fields = ('display_name', 'model_identifier')
