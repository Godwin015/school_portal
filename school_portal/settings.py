from dotenv import load_dotenv
import os
from pathlib import Path
import dj_database_url

# ===========================
# LOAD ENVIRONMENT VARIABLES
# ===========================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
# SECURITY & DEBUG SETTINGS
# ===========================
SECRET_KEY = os.getenv('SECRET_KEY', 'sk_live_27cba69033dad02cddfe327b9c27aa1063fbd8b9')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Set your Render domain later for security
ALLOWED_HOSTS = ['*']

# ===========================
# INSTALLED APPS
# ===========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'payments',  # your custom app
]

# ===========================
# MIDDLEWARE
# ===========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===========================
# URLS & WSGI
# ===========================
ROOT_URLCONF = 'school_portal.urls'
WSGI_APPLICATION = 'school_portal.wsgi.application'

# ===========================
# EMAIL CONFIGURATION
# ===========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'accounts@schoolname.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your_app_password')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ===========================
# DATABASE CONFIGURATION (PostgreSQL for Render)
# ===========================
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        ssl_require=True
    )
}

# ===========================
# STATIC FILES CONFIGURATION
# ===========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# ===========================
# TEMPLATES CONFIGURATION
# ===========================
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
            ],
        },
    },
]

# ===========================
# FLUTTERWAVE API KEYS
# ===========================
FLW_PUBLIC_KEY = os.getenv("FLW_PUBLIC_KEY")
FLW_SECRET_KEY = os.getenv("FLW_SECRET_KEY")
FLW_BASE_URL = os.getenv("FLW_BASE_URL", "https://api.flutterwave.com/v3")

# ===========================
# DEFAULT AUTO FIELD
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================
# LOGIN / LOGOUT REDIRECTS
# ===========================
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/'
