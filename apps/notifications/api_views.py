from rest_framework import views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notification, Announcement
from .serializers import NotificationSerializer, AnnouncementSerializer

class APINotificationListView(views.APIView):
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)[:25]
        return Response(NotificationSerializer(notifications, many=True).data)

class APINotificationMarkReadView(views.APIView):
    def post(self, request, pk):
        n = get_object_or_404(Notification, id=pk, user=request.user)
        n.is_read = True
        n.save()
        return Response({'status': 'marked as read'})

class APINotificationMarkAllReadView(views.APIView):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all marked as read'})

class APIAnnouncementListView(views.APIView):
    def get(self, request):
        announcements = Announcement.objects.filter(is_active=True)[:5]
        return Response(AnnouncementSerializer(announcements, many=True).data)
