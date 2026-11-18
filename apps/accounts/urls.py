from django.urls import path
from . import views, api_views

app_name = 'accounts'

urlpatterns = [
    # UI URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('verify-email/<str:token>/', views.verify_email_view, name='verify_email'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password_view, name='reset_password'),
    path('export-data/', views.export_user_data_view, name='export_data'),
    path('delete-account/', views.delete_account_view, name='delete_account'),

    # API endpoints
    path('api/auth/register/', api_views.APIRegisterView.as_view(), name='api_register'),
    path('api/auth/login/', api_views.APILoginView.as_view(), name='api_login'),
    path('api/auth/logout/', api_views.APILogoutView.as_view(), name='api_logout'),
    path('api/profile/', api_views.APIProfileView.as_view(), name='api_profile'),
]
