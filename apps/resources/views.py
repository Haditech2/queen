from django.shortcuts import render
from django.db.models import Q
from .models import CrisisResource, MentalHealthResource
from .seed_data import VERIFIED_NIGERIAN_CRISIS_RESOURCES

def ensure_seed_crisis_resources():
    for item in VERIFIED_NIGERIAN_CRISIS_RESOURCES:
        CrisisResource.objects.get_or_create(
            organization=item['organization'],
            phone=item['phone'],
            defaults=item
        )

def crisis_support_view(request):
    ensure_seed_crisis_resources()
    state_filter = request.GET.get('state', '').strip()

    # Prioritize user's state if authenticated and no explicit query
    if not state_filter and request.user.is_authenticated and request.user.state_region:
        user_state = request.user.state_region
        if user_state not in ('Diaspora', 'Other'):
            state_filter = user_state

    qs = CrisisResource.objects.filter(is_verified=True)
    if state_filter and state_filter != 'All':
        qs = qs.filter(Q(location_state__iexact=state_filter) | Q(location_state='Nationwide'))

    resources = qs.order_by('-is_emergency_priority', 'organization')

    available_states = [
        'All', 'Nationwide', 'Lagos', 'FCT', 'Oyo', 'Rivers', 'Enugu', 'Kaduna', 'Kano', 'Ogun', 'Edo', 'Delta'
    ]

    return render(request, 'resources/crisis_support.html', {
        'resources': resources,
        'current_state': state_filter or 'All',
        'available_states': available_states,
    })


def resources_directory_view(request):
    ensure_seed_crisis_resources()
    crisis_resources = CrisisResource.objects.filter(is_verified=True)[:8]
    general_resources = MentalHealthResource.objects.filter(is_verified=True)

    return render(request, 'resources/directory.html', {
        'crisis_resources': crisis_resources,
        'general_resources': general_resources,
    })
