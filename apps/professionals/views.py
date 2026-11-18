from django.shortcuts import render
from django.db.models import Q
from .models import Professional
from .seed_data import VERIFIED_NIGERIAN_PROFESSIONALS

def ensure_seed_professionals():
    for item in VERIFIED_NIGERIAN_PROFESSIONALS:
        Professional.objects.get_or_create(
            name=item['name'],
            state=item['state'],
            defaults=item
        )

def professionals_directory_view(request):
    ensure_seed_professionals()

    # Query params
    state_filter = request.GET.get('state', '').strip()
    category_filter = request.GET.get('category', '').strip()
    mode_filter = request.GET.get('mode', '').strip()
    language_filter = request.GET.get('language', '').strip()
    search_q = request.GET.get('q', '').strip()

    qs = Professional.objects.filter(is_verified=True)

    if state_filter and state_filter != 'All':
        qs = qs.filter(state__iexact=state_filter)

    if category_filter and category_filter != 'All':
        qs = qs.filter(category=category_filter)

    if mode_filter and mode_filter != 'All':
        if mode_filter == 'online':
            qs = qs.filter(Q(consultation_mode='online') | Q(consultation_mode='both'))
        elif mode_filter == 'in_person':
            qs = qs.filter(Q(consultation_mode='in_person') | Q(consultation_mode='both'))

    if language_filter:
        qs = qs.filter(languages_spoken__icontains=language_filter)

    if search_q:
        qs = qs.filter(
            Q(name__icontains=search_q) |
            Q(city__icontains=search_q) |
            Q(services_offered__icontains=search_q) |
            Q(bio__icontains=search_q)
        )

    states_list = ['All', 'Lagos', 'FCT', 'Oyo', 'Ogun', 'Kaduna', 'Enugu', 'Rivers', 'Edo', 'Kano', 'Sokoto']

    return render(request, 'professionals/directory.html', {
        'professionals': qs,
        'state_filter': state_filter or 'All',
        'category_filter': category_filter or 'All',
        'mode_filter': mode_filter or 'All',
        'search_q': search_q,
        'states_list': states_list,
        'categories': Professional.CATEGORY_CHOICES,
        'modes': Professional.MODE_CHOICES,
    })
