from dotenv import load_dotenv
import os
from pathlib import Path
load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')


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


BASE_DIR = Path(__file__).resolve().parent.parent

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

# The directory where Django will collect all static files for deployment
STATIC_ROOT = BASE_DIR / 'staticfiles'

# (Optional) If you have a local static directory for development
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
