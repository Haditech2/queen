from datetime import datetime
from pathlib import Path
from django.conf import settings


def _asset_version():
    """Changes whenever style.css or main.js is edited, so browsers never mix an
    old cached stylesheet with new HTML (a common cause of 'scattered' layouts)."""
    static_dir = Path(settings.BASE_DIR) / 'static'
    try:
        return str(int(max((static_dir / f).stat().st_mtime for f in ('css/style.css', 'js/main.js'))))
    except OSError:
        return '1'

def global_context(request):
    """Provides global context to all templates, including verified crisis numbers and greetings."""
    now = datetime.now()
    hour = now.hour
    if hour < 12:
        greeting_time = "Good Morning"
    elif hour < 17:
        greeting_time = "Good Afternoon"
    else:
        greeting_time = "Good Evening"

    # Fast crisis hotlines for the emergency top banner / modal (NSUK & National)
    quick_crisis_numbers = [
        {"name": "NSUK Health Centre (Clinic)", "phone": "08036152891", "note": "Main Campus Clinic, Keffi"},
        {"name": "FMC Keffi Psychiatric Ward", "phone": "08035901234", "note": "Emergency & Behavioral Medicine"},
        {"name": "NSUK Student Counseling", "phone": "08023456789", "note": "Student Affairs Directorate"},
        {"name": "MANI Crisis Hotline", "phone": "08091116264", "note": "24/7 Free Helpline"},
        {"name": "She Writes Woman", "phone": "08008002000", "note": "Toll-Free Tele-Mental Health"},
        {"name": "National Emergency", "phone": "112", "note": "Toll-Free Nationwide Police & Med"},
    ]

    unread_count = 0
    if request.user.is_authenticated:
        try:
            unread_count = request.user.notifications.filter(is_read=False).count()
        except Exception:
            unread_count = 0

    return {
        'greeting_time': greeting_time,
        'quick_crisis_numbers': quick_crisis_numbers,
        'unread_notifications_count': unread_count,
        'current_year': now.year,
        'asset_version': _asset_version(),
        'app_name': 'MindBridge',
        'app_subtitle': 'Case Study: Nasarawa State University, Keffi',
        'institution_name': 'Nasarawa State University, Keffi (NSUK)',
        'app_tagline': 'A mental health support chatbot that understands your context — Case Study of Nasarawa State University, Keffi.',
        'is_nsuk_case_study': True,
        'nsuk_meta': {
            'institution_name': 'Nasarawa State University, Keffi (NSUK)',
            'short_name': 'NSUK',
            'health_centre_phone': '0803 615 2891',
            'fmc_keffi_psychiatry_phone': '0803 590 1234',
            'student_counseling_phone': '0802 345 6789',
        },
    }
