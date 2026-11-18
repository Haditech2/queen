from django.utils import timezone
from django.db.models import Count
from apps.accounts.models import CustomUser
from apps.conversations.models import Conversation, Message
from apps.screening.models import ScreeningSession
from apps.safety.models import SafetyEvent
from .models import AggregatedDailyMetric

def compile_daily_metrics():
    today = timezone.now().date()
    total_users = CustomUser.objects.count()
    total_convs = Conversation.objects.count()
    msgs_today = Message.objects.filter(created_at__date=today).count()
    crisis_today = SafetyEvent.objects.filter(timestamp__date=today, risk_level__in=['HIGH', 'IMMINENT']).count()
    screenings_today = ScreeningSession.objects.filter(completed_at__date=today).count()

    lang_counts = dict(CustomUser.objects.values_list('preferred_language').annotate(c=Count('id')))

    metric, _ = AggregatedDailyMetric.objects.update_or_create(
        date=today,
        defaults={
            'total_registered_users': total_users,
            'total_conversations': total_convs,
            'messages_sent_today': msgs_today,
            'crisis_interventions_count': crisis_today,
            'screenings_completed_today': screenings_today,
            'top_languages_distribution': lang_counts,
        }
    )
    return metric
