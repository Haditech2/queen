from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import MoodCheckIn
from .forms import MoodCheckInForm

@login_required
def mood_dashboard_view(request):
    today = timezone.now().date()
    today_checkin = MoodCheckIn.objects.filter(user=request.user, created_at__date=today).first()

    if request.method == 'POST':
        form = MoodCheckInForm(request.POST, instance=today_checkin)
        if form.is_valid():
            checkin = form.save(commit=False)
            checkin.user = request.user
            checkin.save()
            messages.success(request, f"Your emotional check-in ({checkin.get_mood_display()}) was recorded safely.")
            return redirect('mood:dashboard')
    else:
        form = MoodCheckInForm(instance=today_checkin)

    recent_checkins = MoodCheckIn.objects.filter(user=request.user)[:30]

    # Calculate average stress and mood distribution for privacy-first charts
    stress_scores = [c.stress_level for c in recent_checkins if c.stress_level]
    avg_stress = round(sum(stress_scores) / len(stress_scores), 1) if stress_scores else 5.0

    # Split the "<emoji> <Word>" choice labels so the UI can render mood tiles.
    mood_options = []
    for value, label in MoodCheckIn.MOOD_CHOICES:
        parts = label.split(' ', 1)
        mood_options.append({
            'value': value,
            'emoji': parts[0],
            'label': parts[1] if len(parts) > 1 else label,
        })

    return render(request, 'mood/dashboard.html', {
        'form': form,
        'today_checkin': today_checkin,
        'recent_checkins': recent_checkins,
        'avg_stress': avg_stress,
        'checkin_count': recent_checkins.count(),
        'mood_options': mood_options,
    })
