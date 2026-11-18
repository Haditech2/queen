from django.urls import path
from . import views, api_views

app_name = 'mood'

urlpatterns = [
    path('mood/', views.mood_dashboard_view, name='dashboard'),
    path('api/mood/', api_views.APIMoodCheckInListCreateView.as_view(), name='api_mood_checkin'),
]
