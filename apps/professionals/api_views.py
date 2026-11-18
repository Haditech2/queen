from rest_framework import views, permissions
from rest_framework.response import Response
from django.db.models import Q
from .models import Professional
from .serializers import ProfessionalSerializer
from .views import ensure_seed_professionals

class APIProfessionalListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        ensure_seed_professionals()
        state = request.GET.get('state')
        category = request.GET.get('category')
        mode = request.GET.get('mode')
        query = request.GET.get('q')

        qs = Professional.objects.filter(is_verified=True)
        if state and state != 'All':
            qs = qs.filter(state__iexact=state)
        if category and category != 'All':
            qs = qs.filter(category=category)
        if mode and mode != 'All':
            if mode == 'online':
                qs = qs.filter(Q(consultation_mode='online') | Q(consultation_mode='both'))
            elif mode == 'in_person':
                qs = qs.filter(Q(consultation_mode='in_person') | Q(consultation_mode='both'))
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(services_offered__icontains=query) | Q(city__icontains=query))

        return Response(ProfessionalSerializer(qs, many=True).data)
