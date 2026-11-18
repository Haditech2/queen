from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from apps.chatbot.service import ChatbotSafetyPipeline

class APIConversationListCreateView(views.APIView):
    def get(self, request):
        convs = Conversation.objects.filter(user=request.user, is_archived=False)
        return Response(ConversationSerializer(convs, many=True).data)

    def post(self, request):
        title = request.data.get('title', 'New Chat')
        lang = request.data.get('language', request.user.preferred_language)
        conv = Conversation.objects.create(user=request.user, title=title, language=lang)
        return Response(ConversationSerializer(conv).data, status=status.HTTP_201_CREATED)


class APIConversationDetailView(views.APIView):
    def get(self, request, pk):
        conv = get_object_or_404(Conversation, id=pk, user=request.user)
        return Response(ConversationSerializer(conv).data)

    def patch(self, request, pk):
        conv = get_object_or_404(Conversation, id=pk, user=request.user)
        if 'title' in request.data:
            conv.title = request.data['title'][:150]
        if 'language' in request.data:
            conv.language = request.data['language']
        conv.save()
        return Response(ConversationSerializer(conv).data)

    def delete(self, request, pk):
        conv = get_object_or_404(Conversation, id=pk, user=request.user)
        conv.delete()
        return Response({'message': 'Conversation deleted'}, status=status.HTTP_204_NO_CONTENT)


class APIChatSendMessageView(views.APIView):
    """
    Core Chat Endpoint:
    Receives user message -> Passes through safety pipeline -> Saves user and assistant messages -> Returns JSON.
    """
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'chat'
    def post(self, request):
        content = str(request.data.get('message') or '').strip()
        conversation_id = request.data.get('conversation_id')
        session_language = request.data.get('language') or request.user.preferred_language

        if not content:
            return Response({'error': 'Message cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve or create conversation
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        else:
            first_words = " ".join(content.split()[:5])
            conversation = Conversation.objects.create(
                user=request.user,
                title=first_words if first_words else "New Chat",
                language=session_language
            )

        # Build conversation history from the 10 MOST RECENT messages (oldest first),
        # skipping system/safety rows the LLM should not see as dialogue turns.
        recent = conversation.messages.filter(role__in=('user', 'assistant')).order_by('-created_at')[:10]
        past_msgs = [{'role': m.role, 'content': m.content} for m in reversed(list(recent))]

        # Execute Safety & AI Pipeline
        pipeline = ChatbotSafetyPipeline()
        result = pipeline.process_message(
            user_message=content,
            user=request.user,
            conversation_history=past_msgs,
            session_language=session_language,
            session_id=str(conversation.id)
        )

        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=content,
            risk_level=result['risk_level']
        )

        # Save assistant response
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=result['content'],
            risk_level=result['risk_level']
        )

        # Update conversation title if it was default
        if conversation.title in ('New Chat', 'New Reflection') and len(content) > 3:
            summary = " ".join(content.split()[:5])
            conversation.title = (summary[:40] + '...') if len(summary) > 40 else summary
        conversation.save()  # bumps updated_at so the chat moves to the top of the sidebar

        return Response({
            'conversation_id': str(conversation.id),
            'conversation_title': conversation.title,
            'user_message': MessageSerializer(user_msg).data,
            'assistant_message': MessageSerializer(assistant_msg).data,
            'risk_level': result['risk_level'],
            'is_crisis': result['is_crisis'],
            'category': result['category']
        })


class APIReportMessageView(views.APIView):
    def post(self, request, message_id):
        msg = get_object_or_404(Message, id=message_id, conversation__user=request.user)
        reason = request.data.get('reason', 'User reported response')
        msg.is_reported = True
        msg.report_reason = reason[:255]
        msg.save()
        return Response({'status': 'Report received. Thank you for helping keep MindBridge safe and helpful.'})
