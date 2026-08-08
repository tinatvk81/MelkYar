"""
تنظیمات پروژه ملک‌یار (MelkYar) — سامانه مدیریت فایل‌های املاک

نکته‌ی امنیتی مهم: هیچ مقدار حساسی (SECRET_KEY، رمز دیتابیس، ...) نباید
داخل این فایل هارد‌کد شود. همه از فایل .env (که در .gitignore است و
هرگز commit نمی‌شود) خوانده می‌شوند. یک نمونه در .env.example هست.
"""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(key, default=False):
    return os.environ.get(key, str(default)) == "True"


def env_list(key, default=""):
    raw = os.environ.get(key, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


# --- امنیت -------------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY تنظیم نشده. یک مقدار تصادفی در فایل .env بگذارید "
        "(می‌توانید با: python -c \"import secrets; print(secrets.token_urlsafe(50))\" بسازید)."
    )

DEBUG = env_bool("DEBUG", default=False)  # پیش‌فرض False؛ فقط در توسعه صراحتاً True کنید
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")

if not DEBUG and (not ALLOWED_HOSTS or ALLOWED_HOSTS == ["*"]):
    raise RuntimeError("در حالت DEBUG=False باید ALLOWED_HOSTS دقیقاً دامنه‌های واقعی را داشته باشد، نه *.")

# --- هدرهای امنیتی HTTP (فعال فقط وقتی پشت HTTPS واقعی هستید، یعنی DEBUG=False) ---
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # فرانت‌اند React برای هدر CSRF نیاز به خواندنش دارد
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000  # ۱ سال، فقط در production
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
# اگر پشت nginx/Cloudflare با ترمینیشن SSL هستید، این را هم لازم دارید:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- اپلیکیشن‌ها ---------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",  # امکان باطل کردن توکن هنگام خروج/غیرفعال‌سازی
    "django_filters",
    "corsheaders",
    "axes",  # قفل موقت اکانت بعد از چند بار رمز اشتباه (Brute-force protection)
    # local apps
    "accounts",
    "properties",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",  # باید آخرین middleware باشد
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",  # اول چک می‌کند اکانت قفل نیست
    "django.contrib.auth.backends.ModelBackend",
]

# --- محدودیت تلاش‌های ورود ناموفق (ضد Brute-force) -----------------------
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCKOUT_PARAMETERS = ["username"]
AXES_RESET_ON_SUCCESS = True

# --- CORS: فقط دامنه‌های فرانت‌اند واقعی خودتان را اینجا اضافه کنید ------
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "melkyar.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "melkyar.wsgi.application"

# --- پایگاه داده ---------------------------------------------------------
# اگر DB_ENGINE=postgresql در .env تنظیم شود، به‌جای SQLite از پستگرس با
# اطلاعات اتصال گرفته‌شده از متغیرهای محیطی استفاده می‌شود (رمز هرگز در کد نیست).
if os.environ.get("DB_ENGINE") == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- زبان و منطقه (فارسی/تهران) -----------------------------------------
LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Django REST Framework ------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # محدودیت نرخ درخواست، هم برای کاربران ناشناس (مثلاً تلاش‌های ورود) و هم
    # کاربران وارد‌شده، تا از سوءاستفاده/اسکرپینگ فایل‌ها جلوگیری شود.
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "20/minute",
        "user": "120/minute",
    },
}

SIMPLE_JWT = {
    # عمر کوتاه‌تر access token + امکان blacklist کردن refresh token هنگام
    # خروج یا غیرفعال‌سازی اکانت مشاور (با app توکن_blacklist که بالا اضافه شد)
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

# --- محدودیت فایل‌های آپلودی (برای گالری تصاویر) --------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# --- لاگ‌گیری (برای ردیابی خطا و تلاش‌های مشکوک در production) -------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "melkyar.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
        },
    },
    "root": {"handlers": ["console", "file"], "level": "WARNING"},
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
        "django.security": {"handlers": ["console", "file"], "level": "WARNING", "propagate": False},
    },
}
