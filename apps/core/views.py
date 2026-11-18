import os

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.conf import settings
from pathlib import Path
from apps.mood.models import MoodCheckIn
from apps.conversations.models import Conversation
from apps.coping.models import CopingTool
from apps.coping.views import ensure_seed_tools
from apps.resources.models import CrisisResource
from apps.resources.views import ensure_seed_crisis_resources
from apps.notifications.models import Announcement
from apps.screening.models import ScreeningSession

def landing_page_view(request):
    if request.user.is_authenticated:
        return redirect('conversations:chat')

    ensure_seed_crisis_resources()
    ensure_seed_tools()
    crisis_hotlines = CrisisResource.objects.filter(is_verified=True, is_emergency_priority=True)[:4]
    sample_tools = CopingTool.objects.filter(is_active=True)[:3]

    return render(request, 'core/landing.html', {
        'crisis_hotlines': crisis_hotlines,
        'sample_tools': sample_tools,
    })


def about_view(request):
    return render(request, 'core/about.html')


def robots_txt_view(request):
    """Serve robots.txt from the project root so crawlers find it at /robots.txt."""
    robots_path = Path(settings.BASE_DIR) / 'static' / 'robots.txt'
    try:
        body = robots_path.read_text(encoding='utf-8')
    except OSError:
        body = "User-agent: *\nAllow: /\n"
    return HttpResponse(body, content_type='text/plain')


def privacy_policy_view(request):
    return render(request, 'core/privacy.html')


def terms_of_service_view(request):
    return render(request, 'core/terms.html')


def health_check_view(request):
    """Lightweight deployment diagnostics (no secrets, no chat data)."""
    from apps.accounts.models import CustomUser

    info = {
        'status': 'ok',
        'debug': settings.DEBUG,
        'database_engine': connection.vendor,
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()

        tables = set(connection.introspection.table_names())
        info['database'] = 'reachable'
        info['migrations_applied'] = 'django_migrations' in tables
        info['user_table_ready'] = CustomUser._meta.db_table in tables
        if info['user_table_ready']:
            info['admin_user_exists'] = CustomUser.objects.filter(
                email=os.getenv('ADMIN_EMAIL', 'admin@mindbridge.africa')
            ).exists()
    except Exception as exc:  # pragma: no cover - diagnostic path
        info['status'] = 'error'
        info['database'] = 'unreachable'
        info['error_type'] = type(exc).__name__

    return JsonResponse(info, status=200 if info['status'] == 'ok' else 503)


@login_required
def dashboard_view(request):
    ensure_seed_tools()
    ensure_seed_crisis_resources()

    today = timezone.now().date()
    today_checkin = MoodCheckIn.objects.filter(user=request.user, created_at__date=today).first()
    recent_checkins = MoodCheckIn.objects.filter(user=request.user)[:7]

    recent_conversations = Conversation.objects.filter(user=request.user, is_archived=False)[:5]
    recommended_tools = CopingTool.objects.filter(is_active=True)[:4]
    crisis_resources = CrisisResource.objects.filter(is_verified=True, is_emergency_priority=True)[:3]
    announcements = Announcement.objects.filter(is_active=True)[:2]
    recent_screenings = ScreeningSession.objects.filter(user=request.user)[:3]

    # Mood chart datapoints for last 7 entries
    chart_labels = []
    chart_stress_data = []
    mood_map = {'great': 5, 'good': 4, 'okay': 3, 'low': 2, 'anxious': 2, 'overwhelmed': 1, 'angry': 1}
    chart_mood_data = []

    for c in reversed(list(recent_checkins)):
        chart_labels.append(c.created_at.strftime('%a, %d %b'))
        chart_stress_data.append(c.stress_level)
        chart_mood_data.append(mood_map.get(c.mood, 3))

    # Headline metrics for the dashboard tiles
    all_checkins = MoodCheckIn.objects.filter(user=request.user)
    checkin_count = all_checkins.count()
    avg_stress = None
    if chart_stress_data:
        avg_stress = round(sum(chart_stress_data) / len(chart_stress_data), 1)
    chat_count = Conversation.objects.filter(user=request.user, is_archived=False).count()
    screening_count = ScreeningSession.objects.filter(user=request.user).count()

    return render(request, 'core/dashboard.html', {
        'user': request.user,
        'today_checkin': today_checkin,
        'recent_checkins': recent_checkins,
        'recent_conversations': recent_conversations,
        'recommended_tools': recommended_tools,
        'crisis_resources': crisis_resources,
        'announcements': announcements,
        'recent_screenings': recent_screenings,
        'chart_labels': chart_labels,
        'chart_stress_data': chart_stress_data,
        'chart_mood_data': chart_mood_data,
        'avg_stress': avg_stress,
        'checkin_count': checkin_count,
        'chat_count': chat_count,
        'screening_count': screening_count,
    })
