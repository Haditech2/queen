from rest_framework import views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import CopingTool
from .serializers import CopingToolSerializer
from .views import ensure_seed_tools

class APICopingToolListView(views.APIView):
    def get(self, request):
        ensure_seed_tools()
        tools = CopingTool.objects.filter(is_active=True).order_by('order')
        category = request.GET.get('category')
        if category:
            tools = tools.filter(category=category)
        return Response(CopingToolSerializer(tools, many=True).data)

class APICopingToolDetailView(views.APIView):
    def get(self, request, slug):
        ensure_seed_tools()
        tool = get_object_or_404(CopingTool, slug=slug, is_active=True)
        return Response(CopingToolSerializer(tool).data)
