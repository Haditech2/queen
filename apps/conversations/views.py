import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .models import Conversation, Message
from apps.chatbot.service import ChatbotSafetyPipeline
from apps.core.middleware import AuditLoggingMiddleware

@login_required
def chat_view(request, conversation_id=None):
    user_conversations = Conversation.objects.filter(user=request.user, is_archived=False)[:20]

    current_conversation = None
    if conversation_id:
        current_conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    else:
        # Load most recent conversation or prepare empty state
        current_conversation = user_conversations.first()
        if not current_conversation:
            current_conversation = Conversation.objects.create(
                user=request.user,
                title="New Chat",
                language=request.user.preferred_language
            )

    messages_list = current_conversation.messages.all()

    return render(request, 'conversations/chat.html', {
        'conversations': user_conversations,
        'current_conversation': current_conversation,
        'messages_list': messages_list,
        'user_preferred_lang': request.user.preferred_language,
    })


@login_required
def conversations_list_view(request):
    query = request.GET.get('q', '').strip()
    convs = Conversation.objects.filter(user=request.user, is_archived=False)
    if query:
        convs = convs.filter(Q(title__icontains=query) | Q(messages__content__icontains=query)).distinct()

    return render(request, 'conversations/list.html', {
        'conversations': convs,
        'query': query,
    })


@login_required
def new_conversation_view(request):
    lang = request.GET.get('lang', request.user.preferred_language)
    new_conv = Conversation.objects.create(
        user=request.user,
        title="New Chat",
        language=lang
    )
    return redirect('conversations:chat_detail', conversation_id=new_conv.id)


@login_required
def rename_conversation_view(request, conversation_id):
    conv = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    if request.method == 'POST':
        new_title = request.POST.get('title', '').strip()
        if new_title:
            conv.title = new_title[:150]
            conv.save()
            messages.success(request, "Conversation renamed successfully.")
    return redirect('conversations:chat_detail', conversation_id=conv.id)


@login_required
def delete_conversation_view(request, conversation_id):
    conv = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    if request.method == 'POST':
        conv.delete()
        messages.info(request, "Conversation deleted.")
        return redirect('conversations:chat')
    return redirect('conversations:chat_detail', conversation_id=conv.id)


@login_required
def clear_all_conversations_view(request):
    if request.method == 'POST':
        count = Conversation.objects.filter(user=request.user).count()
        Conversation.objects.filter(user=request.user).delete()
        AuditLoggingMiddleware.log_event(request, 'DELETE_DATA', {'cleared_conversations': count})
        messages.info(request, "All conversations have been permanently cleared.")
    return redirect('conversations:chat')


@login_required
def export_conversation_view(request, conversation_id):
    conv = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    output = [f"# MindBridge Conversation: {conv.title}", f"Date: {conv.created_at:%Y-%m-%d %H:%M:%S}\n"]

    for msg in conv.messages.all():
        speaker = "You" if msg.role == 'user' else "MindBridge"
        output.append(f"### {speaker} ({msg.created_at:%H:%M})")
        output.append(f"{msg.content}\n")

    output.append("\n---\n*MindBridge provides supportive listening and is not a substitute for human professional healthcare.*")

    response = HttpResponse("\n".join(output), content_type='text/markdown')
    response['Content-Disposition'] = f'attachment; filename="mindbridge_conversation_{conv.id}.md"'
    return response
