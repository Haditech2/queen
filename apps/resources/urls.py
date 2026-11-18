from django.urls import path
from . import views, api_views

app_name = 'resources'

urlpatterns = [
    # UI URLs
    path('crisis-support/', views.crisis_support_view, name='crisis_support'),
    path('resources/', views.resources_directory_view, name='directory'),

    # API endpoints
    path('api/crisis/', api_views.APICrisisResourceListView.as_view(), name='api_crisis'),
    path('api/resources/', api_views.APIMentalHealthResourceListView.as_view(), name='api_resources'),
]
