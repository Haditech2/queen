from rest_framework import views, permissions
from rest_framework.response import Response
from django.db.models import Q
from .models import CrisisResource, MentalHealthResource
from .serializers import CrisisResourceSerializer, MentalHealthResourceSerializer
from .views import ensure_seed_crisis_resources

class APICrisisResourceListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        ensure_seed_crisis_resources()
        state = request.GET.get('state')
        qs = CrisisResource.objects.filter(is_verified=True)
        if state and state != 'All':
            qs = qs.filter(Q(location_state__iexact=state) | Q(location_state='Nationwide'))
        return Response(CrisisResourceSerializer(qs, many=True).data)

class APIMentalHealthResourceListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        qs = MentalHealthResource.objects.filter(is_verified=True)
        return Response(MentalHealthResourceSerializer(qs, many=True).data)
