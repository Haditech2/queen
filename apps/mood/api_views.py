from rest_framework import views, status
from rest_framework.response import Response
from django.utils import timezone
from .models import MoodCheckIn
from .serializers import MoodCheckInSerializer

class APIMoodCheckInListCreateView(views.APIView):
    def get(self, request):
        checkins = MoodCheckIn.objects.filter(user=request.user)[:30]
        return Response(MoodCheckInSerializer(checkins, many=True).data)

    def post(self, request):
        serializer = MoodCheckInSerializer(data=request.data)
        if serializer.is_valid():
            checkin = serializer.save(user=request.user)
            return Response(MoodCheckInSerializer(checkin).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
