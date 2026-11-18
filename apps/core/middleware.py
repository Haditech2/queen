import logging
from .models import AuditLog

logger = logging.getLogger(__name__)

class AuditLoggingMiddleware:
    """Middleware that captures high-level audit events without storing private health text."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def log_event(request, action, details=None):
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')

            user = request.user if request.user.is_authenticated else None
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

            AuditLog.objects.create(
                action=action,
                user=user,
                ip_address=ip,
                user_agent=user_agent,
                details=details or {}
            )
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
