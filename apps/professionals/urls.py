from django.urls import path
from . import views, api_views

app_name = 'professionals'

urlpatterns = [
    # UI URLs
    path('professionals/', views.professionals_directory_view, name='directory'),

    # API
    path('api/professionals/', api_views.APIProfessionalListView.as_view(), name='api_professionals'),
]
