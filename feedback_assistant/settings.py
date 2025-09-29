"""
Django settings for feedback_assistant project.

Compatível com Django 5.2.6.
- Local: DEBUG=1, SQLite por padrão.
- Produção (ex.: Render): DEBUG=0, DATABASE_URL (Postgres), WhiteNoise p/ estáticos.
"""

from pathlib import Path
import os
import dj_database_url

# =========================
# Helpers
# =========================
def env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "t", "yes", "y", "on"}

def env_list(name: str, default_csv: str = "") -> list[str]:
    raw = os.environ.get(name, default_csv)
    return [item.strip() for item in raw.split(",") if item.strip()]

# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Básico / Ambiente
# =========================
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-unsafe-change-me")
DEBUG = env_bool("DEBUG", default=True)

# Hosts e CSRF (podem ser sobrescritos por env)
ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    default_csv="127.0.0.1,localhost"
)
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    # incluo local e ngrok por padrão; em produção (Render) setar ex.: https://seu-servico.onrender.com
    default_csv="http://127.0.0.1:8000,http://localhost:8000,https://*.ngrok-free.app,https://*.ngrok-free.dev"
)

# =========================
# Apps
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "feedbacks",
]

# =========================
# Middleware
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise: servir arquivos estáticos em produção
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "feedback_assistant.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # usar templates dos apps (APP_DIRS=True)
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

WSGI_APPLICATION = "feedback_assistant.wsgi.application"

# =========================
# Database
# - Usa DATABASE_URL se existir (Postgres em PaaS como Render)
# - Fallback p/ SQLite local
# =========================
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=int(os.environ.get("DB_CONN_MAX_AGE", "600")),
        ssl_require=env_bool("DB_SSL_REQUIRE", default=not DEBUG),
    )
}

# =========================
# Password validation
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =========================
# I18N / Timezone
# =========================
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "pt-br")
TIME_ZONE = os.environ.get("TIME_ZONE", "America/Fortaleza")
USE_I18N = True
USE_TZ = True

# =========================
# Static files
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Django 5: STORAGES com WhiteNoise (manifest + compress)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# =========================
# Segurança (ajustes padrões para produção)
# =========================
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", default=not DEBUG)
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", default=not DEBUG)
X_FRAME_OPTIONS = os.environ.get("X_FRAME_OPTIONS", "DENY")
SECURE_REFERRER_POLICY = os.environ.get("SECURE_REFERRER_POLICY", "same-origin")
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=not DEBUG)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", default=False)  # habilite se usar HSTS preload

# =========================
# PK padrão
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
