from django.urls import path
from . import views, api_views

app_name = 'coping'

urlpatterns = [
    # UI URLs
    path('coping-tools/', views.coping_list_view, name='list'),
    path('coping-tools/<slug:slug>/', views.coping_detail_view, name='detail'),

    # API
    path('api/coping-tools/', api_views.APICopingToolListView.as_view(), name='api_coping_list'),
    path('api/coping-tools/<slug:slug>/', api_views.APICopingToolDetailView.as_view(), name='api_coping_detail'),
]
