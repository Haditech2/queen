from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ScreeningTool, ScreeningSession, ScreeningResponse
from .questionnaires import QUESTIONNAIRE_DEFINITIONS
from apps.core.middleware import AuditLoggingMiddleware

@login_required
def screening_list_view(request):
    past_sessions = ScreeningSession.objects.filter(user=request.user)[:15]
    tools = QUESTIONNAIRE_DEFINITIONS

    return render(request, 'screening/list.html', {
        'tools': tools,
        'past_sessions': past_sessions,
    })


@login_required
def screening_detail_view(request, tool_type):
    tool_key = tool_type.upper()
    if tool_key not in QUESTIONNAIRE_DEFINITIONS:
        messages.error(request, "Selected questionnaire not found.")
        return redirect('screening:list')

    definition = QUESTIONNAIRE_DEFINITIONS[tool_key]
    db_tool, _ = ScreeningTool.objects.get_or_create(
        tool_type=tool_key,
        defaults={
            'name': definition['name'],
            'description': definition['description'],
            'instructions': definition['instructions'],
        }
    )

    if request.method == 'POST':
        consent = request.POST.get('consent') == 'on'
        questions = definition['questions']
        options = definition['options']

        total_score = 0
        responses_data = []
        harm_flag = False

        for idx, q_text in enumerate(questions):
            val_str = request.POST.get(f'q_{idx}', '0')
            try:
                val = int(val_str)
            except ValueError:
                val = 0

            # Find matching label
            matched_label = next((opt['label'] for opt in options if opt['value'] == val), "")
            total_score += val
            responses_data.append({
                'index': idx + 1,
                'text': q_text,
                'value': val,
                'label': matched_label
            })

            # Check if PHQ-9 question 9 (suicidal ideation/self-harm item) was endorsed
            if tool_key == 'PHQ9' and idx == 8 and val > 0:
                harm_flag = True

        severity_label, interpretation = definition['scoring'](total_score)

        session = None
        if consent:
            session = ScreeningSession.objects.create(
                user=request.user,
                tool=db_tool,
                total_score=total_score,
                severity_label=severity_label,
                interpretation=interpretation,
                has_consented_storage=True
            )
            for r in responses_data:
                ScreeningResponse.objects.create(
                    session=session,
                    question_index=r['index'],
                    question_text=r['text'],
                    selected_value=r['value'],
                    selected_label=r['label']
                )
            AuditLoggingMiddleware.log_event(
                request,
                'SCREENING_COMPLETED',
                {'tool': tool_key, 'score': total_score, 'severity': severity_label}
            )

        return render(request, 'screening/results.html', {
            'definition': definition,
            'total_score': total_score,
            'severity_label': severity_label,
            'interpretation': interpretation,
            'session': session,
            'saved': consent,
            'harm_flag': harm_flag,
        })

    return render(request, 'screening/detail.html', {
        'tool_key': tool_key,
        'definition': definition,
    })
