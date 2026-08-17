import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# ================================================================
# BASE DIRECTORIES
# ================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "apps"))

load_dotenv(dotenv_path=BASE_DIR / ".env")

# ================================================================
# SECURITY
# ================================================================
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-vitalis-mvp-dev-key-troque-em-producao",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "TRUE").upper() == "TRUE"

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [
        host for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if host
    ]

# ================================================================
# APPS
# ================================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps
    "apps.common",
    "apps.notification",
    "apps.scheduling",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# ================================================================
# TEMPLATES
# ================================================================
APPS_DIR = BASE_DIR / "apps"

WEB_TEMPLATE_DIRS = [
    app / "web" / "templates"
    for app in APPS_DIR.iterdir()
    if (app / "web" / "templates").exists()
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": WEB_TEMPLATE_DIRS,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ================================================================
# DATABASE (SQLite)
# ================================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / os.environ.get("DB_NAME", "db.sqlite3"),
    }
}

if "test" in sys.argv:
    DATABASES["default"]["NAME"] = ":memory:"

# ================================================================
# AUTH
# ================================================================
AUTH_USER_MODEL = "scheduling.Therapist"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "admin:login"
LOGIN_REDIRECT_URL = "scheduling:home"
LOGOUT_REDIRECT_URL = "scheduling:home"

# ================================================================
# INTERNATIONALIZATION & TIMEZONE
# ================================================================
LANGUAGE_CODE = "pt-br"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "America/Recife")
USE_I18N = True
USE_TZ = True

# ================================================================
# STATIC & MEDIA FILES
# ================================================================
STATIC_URL = "static/"
STATICFILES_DIRS = [
    p for p in (BASE_DIR / "apps").glob("*/web/static") if p.is_dir()
]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ================================================================
# EMAIL CONFIGURATION
# ================================================================
# Baseado na configuração do proage-interno (core/settings.py), simplificado
# para MVP: sem SMTP configurado (DJANGO_EMAIL_HOST vazio), cai para o backend
# de console — os e-mails são impressos no terminal do `runserver`, sem
# precisar de servidor SMTP para testar o disparo de notificações.
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "")
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD", "")

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST
    else "django.core.mail.backends.console.EmailBackend"
)

EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("DJANGO_EMAIL_USE_TLS", "TRUE").upper() == "TRUE"
EMAIL_USE_SSL = os.environ.get("DJANGO_EMAIL_USE_SSL", "FALSE").upper() == "TRUE"
EMAIL_TIMEOUT = 10

DEFAULT_FROM_EMAIL = os.environ.get("DJANGO_DEFAULT_FROM_EMAIL", "no-reply@vitalis.local")
