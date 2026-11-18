from django.urls import path
from . import api_views

app_name = 'notifications'

urlpatterns = [
    path('api/notifications/', api_views.APINotificationListView.as_view(), name='api_notifications'),
    path('api/notifications/<uuid:pk>/read/', api_views.APINotificationMarkReadView.as_view(), name='api_notification_read'),
    path('api/notifications/read-all/', api_views.APINotificationMarkAllReadView.as_view(), name='api_notifications_read_all'),
    path('api/announcements/', api_views.APIAnnouncementListView.as_view(), name='api_announcements'),
]
