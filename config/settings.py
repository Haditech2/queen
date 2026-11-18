import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / '.env')

# Vercel sets VERCEL=1 in both the build and the runtime environment.
ON_VERCEL = bool(os.getenv('VERCEL'))

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-mindbridge-dev-secret-key-change-in-prod')

DEBUG = os.getenv('DEBUG', 'False' if ON_VERCEL else 'True').lower() in ('true', '1', 't')

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]').split(',') if host.strip()]
if ON_VERCEL:
    # Production + preview deployments (e.g. queen-abc123.vercel.app).
    ALLOWED_HOSTS.append('.vercel.app')

# Trust HTTPS requests forwarded by Vercel's edge network.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Origins allowed to submit POST forms (login, register, chat API).
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]
if ON_VERCEL:
    CSRF_TRUSTED_ORIGINS.append('https://*.vercel.app')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',

    # Local Apps
    'apps.core.apps.CoreConfig',
    'apps.accounts.apps.AccountsConfig',
    'apps.safety.apps.SafetyConfig',
    'apps.chatbot.apps.ChatbotConfig',
    'apps.conversations.apps.ConversationsConfig',
    'apps.mood.apps.MoodConfig',
    'apps.screening.apps.ScreeningConfig',
    'apps.coping.apps.CopingConfig',
    'apps.professionals.apps.ProfessionalsConfig',
    'apps.resources.apps.ResourcesConfig',
    'apps.notifications.apps.NotificationsConfig',
    'apps.analytics.apps.AnalyticsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.AuditLoggingMiddleware',
    'apps.safety.middleware.AISafetySecurityHeadersMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
# Supports PostgreSQL via DATABASE_URL, with local SQLite fallback for dev
DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR / 'mindbridge.sqlite3'}")
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        # Serverless functions are frozen between requests, so pooled
        # connections should not be reused across invocations.
        conn_max_age=int(os.getenv('DB_CONN_MAX_AGE', '0' if ON_VERCEL else '600')),
        conn_health_checks=True,
    )
}

# Required when connecting through a PgBouncer-style pooler (Neon, Supabase).
if DATABASES['default']['ENGINE'].endswith('postgresql'):
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')
TIME_ZONE = os.getenv('TIME_ZONE', 'Africa/Lagos')
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/chat/'
LOGOUT_REDIRECT_URL = '/'

# Email Backend (Console by default for local development / testing)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'MindBridge Support <support@mindbridge.africa>')

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/min',
        'user': '120/min',
        'chat': '30/min',
    },
}

# AI Provider Configuration (gemini, nvidia, deepseek, kimi, glm, openai)
AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini').lower()
AI_MODEL = os.getenv('AI_MODEL', 'gemini-1.5-flash')
AI_BASE_URL = os.getenv('AI_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta/openai')
AI_API_KEY = os.getenv('AI_API_KEY', os.getenv('GEMINI_API_KEY', ''))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', os.getenv('AI_API_KEY', ''))

# Never call the live AI provider from the automated test suite: tests use the
# deterministic offline fallback so they are fast, free and network-independent.
import sys
if len(sys.argv) > 1 and sys.argv[1] == 'test' or 'pytest' in sys.modules:
    AI_API_KEY = ''
    GEMINI_API_KEY = ''

# Privacy & Security Configurations
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # Allows JS to read token for AJAX/Fetch
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1')
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False').lower() in ('true', '1')
DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', '90'))
MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
