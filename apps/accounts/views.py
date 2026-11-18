import uuid
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import (
    RegistrationForm, LoginForm, UserProfileForm,
    CulturalPreferencesForm, PasswordChangeCustomForm
)
from .models import CustomUser, UserProfile
from apps.core.middleware import AuditLoggingMiddleware

def register_view(request):
    if request.user.is_authenticated:
        return redirect('conversations:chat')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.nsuk_status or user.faculty or user.department or user.residence_location:
                user.is_nsuk_affiliate = True
            password = form.cleaned_data['password']
            user.set_password(password)
            user.verification_token = str(uuid.uuid4())
            user.save()

            AuditLoggingMiddleware.log_event(request, 'REGISTER', {'email': user.email})

            # Send verification email or simulate for console backend
            verify_url = request.build_absolute_uri(f"/verify-email/{user.verification_token}/")
            try:
                send_mail(
                    subject="Verify your MindBridge Account",
                    message=f"Welcome {user.first_name},\n\nPlease verify your email for MindBridge by clicking this link:\n{verify_url}\n\nWarm regards,\nThe MindBridge Support Team",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )
            except Exception:
                pass

            # Auto-login newly registered user and take them straight to the chatbot
            login(request, user)
            AuditLoggingMiddleware.log_event(request, 'LOGIN', {'email': user.email, 'source': 'post_registration'})
            messages.success(request, f"Welcome to MindBridge, {user.first_name}! Your chatbot is ready whenever you want to talk.")
            return redirect('conversations:chat')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('conversations:chat')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    AuditLoggingMiddleware.log_event(request, 'LOGIN', {'email': user.email})
                    next_url = request.POST.get('next') or request.GET.get('next')
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    if next_url and url_has_allowed_host_and_scheme(
                        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
                    ):
                        return redirect(next_url)
                    return redirect('conversations:chat')
                else:
                    messages.error(request, "This account is inactive. Please contact support.")
            else:
                messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    AuditLoggingMiddleware.log_event(request, 'LOGOUT', {'email': request.user.email})
    logout(request)
    messages.info(request, "You have been safely signed out. Take care of yourself.")
    return redirect('core:landing')


def verify_email_view(request, token):
    user = CustomUser.objects.filter(verification_token=token).first()
    if user:
        user.is_verified = True
        user.verification_token = ''
        user.save()
        messages.success(request, "Your email has been verified successfully! You can now log in.")
    else:
        messages.error(request, "Invalid or expired verification token.")
    return redirect('accounts:login')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user = CustomUser.objects.filter(email__iexact=email).first()
        if user:
            reset_token = str(uuid.uuid4())
            user.verification_token = reset_token
            user.save()
            reset_url = request.build_absolute_uri(f"/reset-password/{reset_token}/")
            send_mail(
                subject="Reset Your MindBridge Password",
                message=f"Hello {user.first_name},\n\nYou requested a password reset. Click this link to set a new password:\n{reset_url}\n\nIf you did not request this, please ignore this email.\n\nWarm regards,\nMindBridge",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        messages.info(request, "If an account exists with that email address, a password reset link has been dispatched.")
        return redirect('accounts:login')
    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request, token):
    user = CustomUser.objects.filter(verification_token=token).first()
    if not user:
        messages.error(request, "Invalid or expired password reset link.")
        return redirect('accounts:login')

    if request.method == 'POST':
        p1 = request.POST.get('password')
        p2 = request.POST.get('confirm_password')
        if p1 and p2 and p1 == p2:
            user.set_password(p1)
            user.verification_token = ''
            user.save()
            AuditLoggingMiddleware.log_event(request, 'PASSWORD_CHANGE', {'email': user.email, 'source': 'reset_link'})
            messages.success(request, "Your password has been successfully reset. Please log in.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Passwords did not match. Please try again.")

    return render(request, 'accounts/reset_password.html', {'token': token})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        pref_form = CulturalPreferencesForm(request.POST, instance=profile)

        if user_form.is_valid() and pref_form.is_valid():
            u = user_form.save(commit=False)
            if u.nsuk_status or u.faculty or u.department or u.residence_location:
                u.is_nsuk_affiliate = True
            u.save()
            pref_form.save()
            AuditLoggingMiddleware.log_event(request, 'PROFILE_UPDATE')
            messages.success(request, "Your profile and cultural preferences have been updated.")
            return redirect('accounts:profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        pref_form = CulturalPreferencesForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'pref_form': pref_form,
        'profile': profile
    })


@login_required
def settings_view(request):
    password_form = PasswordChangeCustomForm()

    if request.method == 'POST' and 'change_password' in request.POST:
        password_form = PasswordChangeCustomForm(request.POST)
        if password_form.is_valid():
            if request.user.check_password(password_form.cleaned_data['old_password']):
                request.user.set_password(password_form.cleaned_data['new_password'])
                request.user.save()
                AuditLoggingMiddleware.log_event(request, 'PASSWORD_CHANGE')
                messages.success(request, "Your password was updated successfully. Please keep it secure.")
                return redirect('accounts:settings')
            else:
                messages.error(request, "Your current password was entered incorrectly.")

    return render(request, 'accounts/settings.html', {
        'password_form': password_form,
    })


@login_required
def export_user_data_view(request):
    """Exports all personal user data in clean JSON format (conversations, mood history, screenings)."""
    user = request.user
    profile = getattr(user, 'profile', None)

    # Gather conversations
    conversations_data = []
    for conv in user.conversations.all():
        messages_data = [
            {
                'role': m.role,
                'content': m.content,
                'timestamp': m.created_at.isoformat(),
                'risk_level': m.risk_level
            }
            for m in conv.messages.all()
        ]
        conversations_data.append({
            'id': str(conv.id),
            'title': conv.title,
            'language': conv.language,
            'created_at': conv.created_at.isoformat(),
            'messages': messages_data
        })

    # Gather mood check-ins
    moods_data = [
        {
            'date': m.created_at.strftime('%Y-%m-%d'),
            'mood': m.mood,
            'stress_level': m.stress_level,
            'sleep_quality': m.sleep_quality,
            'note': m.note
        }
        for m in user.mood_checkins.all()
    ]

    # Gather screenings
    screenings_data = [
        {
            'tool_name': s.tool.name,
            'tool_type': s.tool.tool_type,
            'score': s.total_score,
            'severity_label': s.severity_label,
            'completed_at': s.completed_at.isoformat(),
        }
        for s in user.screening_sessions.all()
    ]

    data = {
        'user': {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone_number,
            'age_range': user.age_range,
            'gender': user.gender,
            'state_region': user.state_region,
            'preferred_language': user.preferred_language,
            'preferred_communication_style': user.preferred_communication_style,
            'support_systems': profile.comfortable_support_systems if profile else [],
            'faith_preference': profile.faith_preference if profile else ''
        },
        'conversations': conversations_data,
        'mood_checkins': moods_data,
        'screenings': screenings_data,
        'exported_at': str(uuid.uuid4())
    }

    AuditLoggingMiddleware.log_event(request, 'EXPORT_DATA')

    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="mindbridge_data_export_{user.first_name}.json"'
    return response


@login_required
def delete_account_view(request):
    """Allows user to permanently wipe their account and all mental health data."""
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_text', '').strip()
        if confirm_text == 'DELETE':
            user = request.user
            AuditLoggingMiddleware.log_event(request, 'DELETE_DATA', {'email': user.email})
            user.delete()
            messages.info(request, "Your MindBridge account and all associated data have been permanently deleted.")
            return redirect('core:landing')
        else:
            messages.error(request, "Please type DELETE to confirm permanent deletion.")

    return render(request, 'accounts/delete_account.html')
