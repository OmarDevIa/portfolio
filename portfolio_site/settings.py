import os
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {'1', 'true', 'yes', 'on'}

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', '')
if not SECRET_KEY or 'insecure' in SECRET_KEY:
    if not env_bool('DEBUG', True):
        raise RuntimeError('SECRET_KEY must be set to a secure value in production. Set it in your .env file.')
    SECRET_KEY = SECRET_KEY or 'django-insecure-dev-only-change-me'
DEBUG = env_bool('DEBUG', True)
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',') if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'portfolio',
]

if importlib.util.find_spec('jazzmin') is not None:
    INSTALLED_APPS.insert(0, 'jazzmin')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'portfolio_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'portfolio_site.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL', False)
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', '10'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'portfolio@localhost')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
CONTACT_RECIPIENT_EMAIL = os.getenv('CONTACT_RECIPIENT_EMAIL', EMAIL_HOST_USER or DEFAULT_FROM_EMAIL)
SITE_URL = os.getenv('SITE_URL', 'https://omar-tech.com').rstrip('/')
GITHUB_PROFILE_URL = os.getenv('GITHUB_PROFILE_URL', '').strip()
GOOGLE_ANALYTICS_ID = os.getenv('GOOGLE_ANALYTICS_ID', '').strip()
GOOGLE_ANALYTICS_DASHBOARD_URL = os.getenv('GOOGLE_ANALYTICS_DASHBOARD_URL', '').strip()
GOOGLE_SITE_VERIFICATION = os.getenv('GOOGLE_SITE_VERIFICATION', '').strip()

JAZZMIN_SETTINGS = {
    'site_title': 'Omar.tech Admin',
    'site_header': 'Omar.tech',
    'site_brand': 'Omar.tech Studio',
    'site_logo': 'img/profile.svg',
    'site_logo_classes': 'img-circle elevation-2',
    'login_logo': 'img/profile.svg',
    'welcome_sign': 'Administration Omar Atta',
    'copyright': 'Omar Atta',
    'search_model': ['portfolio.Project', 'portfolio.ContactMessage'],
    'topmenu_links': [],
    'usermenu_links': [
        {'name': 'Site public', 'url': 'home', 'new_window': True},
        {'name': 'Tableau de bord', 'url': '/admin/tableau-de-bord/'},
    ],
    'show_sidebar': True,
    'navigation_expanded': True,
    'hide_apps': [],
    'order_with_respect_to': ['portfolio', 'portfolio.Project', 'portfolio.Testimonial', 'portfolio.ContactMessage'],
    'custom_links': {
        'portfolio': [
            {
                'name': 'Dashboard admin',
                'url': '/admin/tableau-de-bord/',
                'icon': 'fas fa-gauge-high',
                'new_window': False,
            },
        ] + ([
            {
                'name': 'Google Analytics',
                'url': GOOGLE_ANALYTICS_DASHBOARD_URL,
                'icon': 'fas fa-chart-line',
                'new_window': True,
            }
        ] if GOOGLE_ANALYTICS_DASHBOARD_URL else [])
    },
    'icons': {
        'portfolio.Project': 'fas fa-briefcase',
        'portfolio.Service': 'fas fa-rocket',
        'portfolio.Skill': 'fas fa-brain',
        'portfolio.Tool': 'fas fa-screwdriver-wrench',
        'portfolio.Testimonial': 'fas fa-comment-dots',
        'portfolio.KPI': 'fas fa-chart-simple',
        'portfolio.ContactMessage': 'fas fa-envelope-open-text',
        'auth.user': 'fas fa-user-shield',
        'auth.Group': 'fas fa-users-gear',
    },
    'default_icon_parents': 'fas fa-folder-open',
    'default_icon_children': 'fas fa-circle',
    'custom_css': 'css/admin-jazzmin.css',
    'show_ui_builder': False,
}

JAZZMIN_UI_TWEAKS = {
    'theme': 'flatly',
    'dark_mode_theme': 'darkly',
    'navbar_small_text': False,
    'footer_small_text': False,
    'navbar_fixed': True,
    'sidebar_fixed': True,
    'sidebar_nav_small_text': False,
    'accent': 'accent-orange',
    'navbar': 'navbar-dark',
    'no_navbar_border': False,
    'sidebar': 'sidebar-dark-primary',
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme_switcher': True,
    'button_classes': {
        'primary': 'btn btn-warning',
        'secondary': 'btn btn-outline-secondary',
        'info': 'btn btn-info',
        'warning': 'btn btn-warning',
        'danger': 'btn btn-danger',
        'success': 'btn btn-success',
    },
}

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
