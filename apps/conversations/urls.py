from django.urls import path
from . import views, api_views

app_name = 'conversations'

urlpatterns = [
    # UI URLs
    path('chat/', views.chat_view, name='chat'),
    path('chat/<uuid:conversation_id>/', views.chat_view, name='chat_detail'),
    path('chat/new/', views.new_conversation_view, name='chat_new'),
    path('conversations/', views.conversations_list_view, name='conversations_list'),
    path('conversations/<uuid:conversation_id>/rename/', views.rename_conversation_view, name='rename_conversation'),
    path('conversations/<uuid:conversation_id>/delete/', views.delete_conversation_view, name='delete_conversation'),
    path('conversations/<uuid:conversation_id>/export/', views.export_conversation_view, name='export_conversation'),
    path('conversations/clear-all/', views.clear_all_conversations_view, name='clear_all'),

    # REST API endpoints
    path('api/chat/', api_views.APIChatSendMessageView.as_view(), name='api_chat_send'),
    path('api/conversations/', api_views.APIConversationListCreateView.as_view(), name='api_conversations_list'),
    path('api/conversations/<uuid:pk>/', api_views.APIConversationDetailView.as_view(), name='api_conversation_detail'),
    path('api/messages/<uuid:message_id>/report/', api_views.APIReportMessageView.as_view(), name='api_message_report'),
]
