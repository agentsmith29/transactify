"""
Django settings for transactify_terminal project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
import logging
import logging.config
from rich.logging import RichHandler

from config import CONFIG


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {'rich': {'datefmt': '[%X]', 'format':'[%(name)s] %(message)s'}},
    'handlers': {
        'store_logs_db': {
            'level': 'DEBUG',
            'class': 'transactify_terminal.LogDBHandler.LogDBHandler',
        },
        'richconsole': {
            'level': 'DEBUG',
            'class': 'rich.logging.RichHandler',
            'formatter': 'rich',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'rich',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'root': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
    
}
logging.config.dictConfig(LOGGING)
logging.info("Logging configured.")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%$_5dhp*byaq92$0iz*751&e27y_=ray(kys90(%ppy8e6!nna'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SERVICE_NAME = os.getenv('SERVICE_NAME', 'terminal')
DJANGO_WEB_HOST = os.getenv('DJANGO_WEB_HOST', 'localhost')
STORE_NAME = os.getenv('SERVICE_NAME', 'store')
HOSTNAME = os.getenv('HOSTNAME', 'localhost')
CONTAINER_NAME = os.getenv('CONTAINER_NAME', 'store_db')

ALLOWED_HOSTS = [
    CONFIG.container.HOSTNAME,
    CONFIG.container.CONTAINER_NAME,
    #
    CONFIG.webservice.SERVICE_NAME,
    CONFIG.webservice.SERVICE_WEB_HOST,
    #
    'localhost', '127.0.0.1'
] 
logging.info(f"Allowed hosts: {ALLOWED_HOSTS}.".replace('[','').replace(']',''))


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
    'terminal'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


ROOT_URLCONF = 'transactify_terminal.urls'

STATIC_URL = CONFIG.django.STATIC_URL
STATIC_ROOT = CONFIG.django.STATIC_ROOT

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

WSGI_APPLICATION = 'transactify_terminal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': CONFIG.database.NAME,
        'USER': CONFIG.database.USER,
        'PASSWORD': CONFIG.database.PASSWORD,
        'HOST': CONFIG.database.HOST,
        'PORT': CONFIG.database.PORT,
    },
    # 'USER': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'USER',
    #     'USER': os.getenv('DJANGO_DB_USER', 'default_user'),
    #     'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', 'default_password'),
    #     'HOST': os.getenv('DJANGO_DB_HOST', 'localhost'),
    #     'PORT': os.getenv('DJANGO_DB_PORT', '5432'),
    # },
}

print(f"Database: {DATABASES}.")


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
