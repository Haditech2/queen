from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.landing_page_view, name='landing'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('about/', views.about_view, name='about'),
    path('privacy/', views.privacy_policy_view, name='privacy'),
    path('terms/', views.terms_of_service_view, name='terms'),
    path('robots.txt', views.robots_txt_view, name='robots'),
]
