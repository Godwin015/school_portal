from dotenv import load_dotenv
import os
from pathlib import Path

# ===========================
# LOAD ENVIRONMENT VARIABLES
# ===========================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
# SECURITY & DEBUG SETTINGS
# ===========================
SECRET_KEY = os.getenv('SECRET_KEY', 'sk_live_27cba69033dad02cddfe327b9c27aa1063fbd8b9')
DEBUG = True  # Set to False in production

ALLOWED_HOSTS = ['*']  # You can later restrict to your Render domain

# ===========================
# INSTALLED APPS
# ===========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # ✅ This enables collectstatic
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
EMAIL_HOST_USER = 'accounts@schoolname.com'  # your sender email address
EMAIL_HOST_PASSWORD = 'your_app_password'    # Gmail app password (not your login password)
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ===========================
# DATABASE CONFIGURATION
# ===========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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
# Flutterwave API configuration
FLW_PUBLIC_KEY = os.getenv("FLW_PUBLIC_KEY")
FLW_SECRET_KEY = os.getenv("FLW_SECRET_KEY")
FLW_BASE_URL = os.getenv("FLW_BASE_URL", "https://api.flutterwave.com/v3")


# ===========================
# DEFAULT AUTO FIELD
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




