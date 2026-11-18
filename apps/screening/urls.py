from django.urls import path
from . import views, api_views

app_name = 'screening'

urlpatterns = [
    # UI URLs
    path('screening/', views.screening_list_view, name='list'),
    path('screening/<str:tool_type>/', views.screening_detail_view, name='detail'),

    # API
    path('api/screenings/', api_views.APIScreeningListView.as_view(), name='api_screenings'),
]
