import os
import sys
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# A filled .env supplies local variables. Pytest must not read it, so a
# developer DATABASE_URL cannot redirect the test suite to Postgres.
if "pytest" not in sys.modules:
    load_dotenv(BASE_DIR / ".env")


def _env(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return value or default


def database_from_url(database_url: str) -> dict:
    """Return Django database settings parsed from a PostgreSQL URL."""
    return dj_database_url.parse(
        database_url,
        conn_max_age=600,
        conn_health_checks=True,
    )


def _default_database() -> dict:
    if "pytest" in sys.modules:
        database_url = ""
    else:
        database_url = _env("DATABASE_URL", "")
    if not database_url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    return database_from_url(database_url)


SECRET_KEY = _env("DJANGO_SECRET_KEY", "dev-only-hello-toutous")
DEBUG = _env("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "catalog",
    "cart",
    "contact",
    "pages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cart.context_processors.cart_count",
            ],
        },
    },
]

DATABASES = {"default": _default_database()}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CONTACT_RECIPIENT_EMAIL = _env("DJANGO_CONTACT_RECIPIENT_EMAIL", "hellotoutous@barlords.fr")
DEFAULT_FROM_EMAIL = _env("DJANGO_DEFAULT_FROM_EMAIL", "hellotoutous@barlords.fr")
EMAIL_HOST = _env("DJANGO_EMAIL_HOST", "ssl0.ovh.net")
EMAIL_PORT = int(_env("DJANGO_EMAIL_PORT", "587"))
EMAIL_HOST_USER = _env("DJANGO_EMAIL_HOST_USER", "hellotoutous@barlords.fr")
EMAIL_HOST_PASSWORD = _env("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = _env("DJANGO_EMAIL_USE_TLS", "1") == "1"
# An empty host keeps messages in the process logs. Tests never load .env.
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST
    else "django.core.mail.backends.console.EmailBackend"
)

# Public bucket URL. Credentials stay empty until they are provided.
OVH_S3_ENDPOINT_URL = _env(
    "OVH_S3_ENDPOINT_URL",
    "https://hellotoutous-bucket.s3.rbx.io.cloud.ovh.net",
)
OVH_S3_ACCESS_KEY_ID = _env("OVH_S3_ACCESS_KEY_ID", "")
OVH_S3_SECRET_ACCESS_KEY = _env("OVH_S3_SECRET_ACCESS_KEY", "")
