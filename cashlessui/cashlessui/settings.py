from pathlib import Path
import os

# BASE_DIR is the root directory of the Django project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # Set to False in production

print(f"Allowed hosts: {os.getenv('DJANGO_WEB_HOST', 'localhost')}:{os.getenv('DJANGO_WEB_PORT', '8080')}")
ALLOWED_HOSTS = [
    f"{os.getenv('DJANGO_WEB_HOST', '*')}"
]  # Adjust this for production (e.g., ['yourdomain.com'])




# Application definition
INSTALLED_APPS = [
    'channels',
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Add your custom apps here
    #'store.apps.StoreConfig',
    'cashlessui',
    'store',
]
 
#AUTH_USER_MODEL = 'cashlessui.User'


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://localhost",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    f"http://{os.getenv('DJANGO_WEB_HOST', 'localhost')}",
    f"http://{os.getenv('DJANGO_WEB_HOST', 'localhost')}:{os.getenv('DJANGO_WEB_PORT', '8000')}",
    f"https://{os.getenv('DJANGO_WEB_HOST', 'localhost')}",
    f"https://{os.getenv('DJANGO_WEB_HOST', 'localhost')}:{os.getenv('DJANGO_WEB_PORT', '8000')}",
]

CSRF_FAILURE_VIEW = "cashlessui.views.custom_csrf_failure_view"


# # Middleware adjustments for proxy
# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Handles security headers
    'django.contrib.sessions.middleware.SessionMiddleware',  # Manages session cookies
    'django.middleware.common.CommonMiddleware',  # Handles general request/response operations
    'django.middleware.csrf.CsrfViewMiddleware',  # Protects against CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Links user authentication
    'django.contrib.messages.middleware.MessageMiddleware',  # Adds messaging framework
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Protects against clickjacking
]


#MIDDLEWARE.insert(
#    MIDDLEWARE.index('django.middleware.csrf.CsrfViewMiddleware'),
#    'cashlessui.csfr.DebugCSRFMiddleware',
#)

# Update Django to recognize proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#HTTP_X_CSRFTOKEN = 'X-CSRFToken'

# Static file serving in production
STATIC_URL = '/static/'  # Ensure consistent usage
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"  # Used by collectstatic

# Login and redirect URLs
LOGIN_REDIRECT_URL = '/dashboard/'  # Redirect after login
LOGOUT_REDIRECT_URL = '/'  # Redirect after logout
LOGIN_URL = '/'  # Login page




ROOT_URLCONF = 'cashlessui.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Adjust if you have custom templates
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

WSGI_APPLICATION = 'project_name.wsgi.application'
ASGI_APPLICATION = 'project_name.asgi.application'

# Database
DATABASES = {
       'USER': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'USER',
        'USER': os.getenv('DJANGO_DB_USER', 'default_user'),
        'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', 'default_password'),
        'HOST': os.getenv('DJANGO_DB_HOST', 'localhost'),
        'PORT': os.getenv('DJANGO_DB_PORT', '5432'),
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DJANGO_DB_NAME', 'default_db'),
        'USER': os.getenv('DJANGO_DB_USER', 'default_user'),
        'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', 'default_password'),
        'HOST': os.getenv('DJANGO_DB_HOST', 'localhost'),
        'PORT': os.getenv('DJANGO_DB_PORT', '5432'),
    }
}
DATABASE_ROUTERS = ['cashlessui.db_router.MultiDatabaseRouter']

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration (Optional for debugging)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'store_logs_db': {
            'level': 'DEBUG',
            'class': 'store.custom_logging.StoreLogsDBHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
    
}