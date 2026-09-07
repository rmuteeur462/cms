from pathlib import Path
import os

DATA_UPLOAD_MAX_NUMBER_FIELDS = 500000

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-^w6%&nnkv*ho^xyt4s%+$jxo6g!@vp3&@gc6gc+q8gfgis789g'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '172.16.17.100', '172.16.17.168:1111', '165.99.50.65', 'wod.wsspeshawar.org.pk:4002', 'wod.wsspeshawar.org.pk']



MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

INSTALLED_APPS = [
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dal',
    'dal_select2',
    'import_export',
    'Dashboard',
    'rest_framework',
    'api',

]


FINTECH_API_USERNAME = "wssp_api_user"
FINTECH_API_PASSWORD = "StrongPassword@123"
FINTECH_API_KEY = "X-123ABC456"




X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'Dashboard.middleware.UserActivityTrackingMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Dashboard.middleware.UserActivityLoggerMiddleware',
]

ROOT_URLCONF = 'wssp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'wssp.wsgi.application'

DATABASES = {
    'default': {
       'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wssp_dashboard_7_oct',
       'USER': 'wssp',
       'PASSWORD': '12345678',
       'HOST': 'localhost',
       'PORT': '5432',
    }
}

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'