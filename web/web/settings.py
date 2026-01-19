"""
Django settings for three_d_generate project.
"""

from pathlib import Path
import sys

# =====================================================
# BASE DIRECTORIES
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure project root is importable (ai_engine, data, etc.)
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PROJECT_DIR = BASE_DIR / "recommender_app"

# =====================================================
# SECURITY
# =====================================================
SECRET_KEY = "your-secret-key"   # Development only
DEBUG = True
ALLOWED_HOSTS = []

# =====================================================
# APPLICATIONS
# =====================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "recommender_app",
]

# =====================================================
# MIDDLEWARE
# =====================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =====================================================
# URLS
# =====================================================
ROOT_URLCONF = "web.urls"

# =====================================================
# TEMPLATES
# =====================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [PROJECT_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# =====================================================
# WSGI
# =====================================================
WSGI_APPLICATION = "web.wsgi.application"

# =====================================================
# DATABASE
# =====================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# =====================================================
# PASSWORD VALIDATION
# =====================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =====================================================
# INTERNATIONALIZATION
# =====================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Amman"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =====================================================
# STATIC FILES  ✅ FIXED
# =====================================================
STATIC_URL = "/static/"

# This MUST point to recommender_app/static
STATICFILES_DIRS = [
    BASE_DIR / "recommender_app" / "static",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# For production (collectstatic)
STATIC_ROOT = BASE_DIR / "staticfiles"
# STATIC_ROOT = BASE_DIR / "static"

# =====================================================
# MEDIA FILES (optional)
# =====================================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =====================================================
# DEFAULT PRIMARY KEY
# =====================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
