from rest_framework import views, status
from rest_framework.response import Response
from .models import ScreeningTool, ScreeningSession, ScreeningResponse
from .serializers import ScreeningSessionSerializer
from .questionnaires import QUESTIONNAIRE_DEFINITIONS

class APIScreeningListView(views.APIView):
    def get(self, request):
        sessions = ScreeningSession.objects.filter(user=request.user)
        return Response(ScreeningSessionSerializer(sessions, many=True).data)

    def post(self, request):
        tool_type = request.data.get('tool_type', '').upper()
        answers = request.data.get('answers', []) # List of integers

        if tool_type not in QUESTIONNAIRE_DEFINITIONS:
            return Response({'error': f'Unsupported questionnaire {tool_type}'}, status=status.HTTP_400_BAD_REQUEST)

        definition = QUESTIONNAIRE_DEFINITIONS[tool_type]
        questions = definition['questions']

        if len(answers) != len(questions):
            return Response({'error': f'Expected {len(questions)} answers, received {len(answers)}'}, status=status.HTTP_400_BAD_REQUEST)

        total_score = sum(int(a) for a in answers)
        severity_label, interpretation = definition['scoring'](total_score)

        db_tool, _ = ScreeningTool.objects.get_or_create(
            tool_type=tool_type,
            defaults={'name': definition['name'], 'description': definition['description'], 'instructions': definition['instructions']}
        )

        session = ScreeningSession.objects.create(
            user=request.user,
            tool=db_tool,
            total_score=total_score,
            severity_label=severity_label,
            interpretation=interpretation,
            has_consented_storage=True
        )

        for idx, (q_text, val) in enumerate(zip(questions, answers)):
            ScreeningResponse.objects.create(
                session=session,
                question_index=idx + 1,
                question_text=q_text,
                selected_value=val,
                selected_label=f"Option {val}"
            )

        return Response(ScreeningSessionSerializer(session).data, status=status.HTTP_201_CREATED)
