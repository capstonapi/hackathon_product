"""Base Django settings for the AI News Intelligence backend."""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = BASE_DIR.parent

env = environ.Env()
# The project's environment file lives beside the frontend and backend folders.
environ.Env.read_env(str(PROJECT_DIR / ".env"))

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-secret-key-change-in-production")
DEBUG = env.bool("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "apps.users",
    "apps.articles",
    "apps.chat",
    "apps.sources",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "common.middleware.AuditMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.middleware.RequestIDMiddleware",
    "common.middleware.RateLimitMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Same Postgres connection strategy as capston_end/config.py: blank
# POSTGRES_HOST/PASSWORD falls back to local peer/socket auth.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="labuser_db"),
        "USER": env("POSTGRES_USER", default="labuser"),
        "PASSWORD": env("POSTGRES_PASSWORD", default=""),
        "HOST": env("POSTGRES_HOST", default=""),
        "PORT": env("POSTGRES_PORT", default=""),
    }
}

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = env.list(
    "DJANGO_CORS_ALLOWED_ORIGINS", default=["http://localhost:5173", "http://localhost:3000"]
)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# Local memory cache is safe for a single process. Production must replace it
# with Redis/shared cache before running multiple web workers.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "news-intelligence"}}
API_RATE_LIMIT_PER_MINUTE = env.int("API_RATE_LIMIT_PER_MINUTE", default=60)
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=False)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# --- Pipeline configuration, ported from capston_end/config.py ---------
GNEWS_API_KEY = env("GNEWS_API_KEY", default="")
GEMINI_API_KEY = env("GEMINI_API_KEY", default="")
GNEWS_LANG = env("GNEWS_LANG", default="en")
GNEWS_COUNTRY = env("GNEWS_COUNTRY", default="us")
GEMINI_MODEL = env("GEMINI_MODEL", default="gemini-2.0-flash")
EMBEDDING_MODEL = env("EMBEDDING_MODEL", default="gemini-embedding-001")
EMBEDDING_DIM = env.int("EMBEDDING_DIM", default=768)
SPACY_MODEL = env("SPACY_MODEL", default="en_core_web_sm")
GNEWS_BASE_URL = "https://gnews.io/api/v4"
# Format: Publisher name|article category|official RSS URL.  Values are
# intentionally restricted to publishers in apps.articles.source_policy.
TRUSTED_RSS_FEEDS = env.list("TRUSTED_RSS_FEEDS", default=[
    "BBC News|world|https://feeds.bbci.co.uk/news/rss.xml",
    "NPR|nation|https://feeds.npr.org/1001/rss.xml",
    "The Guardian|world|https://www.theguardian.com/world/rss",
    "CBC News|nation|https://www.cbc.ca/webfeed/rss/rss-topstories",
    "Al Jazeera|world|https://www.aljazeera.com/xml/rss/all.xml",
    "France 24|world|https://www.france24.com/en/rss",
])
REQUEST_DELAY_SECONDS = env.float("REQUEST_DELAY_SECONDS", default=1.0)
MAX_CHARS_FOR_SUMMARY = env.int("MAX_CHARS_FOR_SUMMARY", default=12000)
# Public articles expire from the verified feed after this many days.
ARTICLE_FRESHNESS_DAYS = env.int("ARTICLE_FRESHNESS_DAYS", default=7)
# When enabled, an article from an explicitly allowlisted official or
# reputable publisher is source-verified on ingest.  Keep this disabled for
# deployments that require independent corroboration before publication.
VERIFY_TRUSTED_SOURCES_WITHOUT_CORROBORATION = env.bool(
    "VERIFY_TRUSTED_SOURCES_WITHOUT_CORROBORATION", default=False
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {"()": "common.logging.RequestIDFilter"},
    },
    "formatters": {
        "json": {"()": "common.logging.JSONFormatter"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["request_id"],
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "news_agent": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
