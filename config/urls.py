from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Core pages (Landing, Dashboard, About, Privacy, Terms)
    path('', include('apps.core.urls')),

    # Accounts & Authentication (Register, Login, Profile, Settings)
    path('', include('apps.accounts.urls')),

    # Chat & Conversations
    path('', include('apps.conversations.urls')),

    # Mood Tracker
    path('', include('apps.mood.urls')),

    # Screening & Self-Assessment Questionnaires
    path('', include('apps.screening.urls')),

    # Evidence-Informed Coping Toolkit
    path('', include('apps.coping.urls')),

    # Verified Professionals & Referral Directory
    path('', include('apps.professionals.urls')),

    # Verified Crisis & Mental Health Resources
    path('', include('apps.resources.urls')),

    # Notifications & Announcements
    path('', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
