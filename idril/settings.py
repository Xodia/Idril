# -*- coding: utf8 -*-

from __future__ import unicode_literals
"""
Django settings for idril project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))



'''
Gives the absolute path of x, relative to the root of the project.
Works when we execute "python manage.py", because manage.py is in the root and x is relative to the root.
'''
ABSOLUTE_PATH = lambda x: os.path.abspath(os.path.dirname(x))

MEDIA_ROOT = ABSOLUTE_PATH('media/')
MEDIA_URL = '/media/'

STATIC_URL = '/static/'

LOGIN_URL = '/member/login'

STATIC_ROOT = '/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!$$!bsp86f7_7xyou@&&c*go8&405p$e$ffs0gdnw@o4e!9!2v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

TEMPLATE_DIRS = (
    'templates/'
)

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    'theme': "simple",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
}
    
# Application definition

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.formtools',
    'base',
    'member',
    'project',
    'forum',
    'mangopay_idril',
    'sekizai',
    'tinymce',
    'south',
    'paypal.standard.pdt',
    'payment',
    'bleach',
    'downtime',
    'mangopaysdk',
    'django_iban',
    'celery',
    'sphinx',
    'model_utils',
    'storages',
    'mangopay',
    'manager',
    'legals',
)

MIDDLEWARE_CLASSES = (
    'downtime.middleware.DowntimeMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "sekizai.context_processors.sekizai",
    )

AUTHENTICATION_BACKENDS = (
    'member.backends.EmailLoginBackend',
    #'django.contrib.auth.backends.ModelBackend',
    )

ROOT_URLCONF = 'idril.urls'

WSGI_APPLICATION = 'idril.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
    	## POSTGRESQL ##
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': 'idrildbpsql',
        # 'HOST': '127.0.0.1',
        # 'USER': 'usrpsql',
        # 'PASSWORD': 'usrpsql',
        # 'PORT':'5432',
	
        # MYSQL ##
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'idrildb',
         'HOST': '127.0.0.1',
         'USER': 'root',
         'PASSWORD': '',
         'PORT':'3306',
    }
}

DOWNTIME_EXEMPT_PATHS = (
    '/admin',# Path not down when maintenance
)

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Payment settings

PAYPAL_RECEIVER_EMAIL = "PAYPAL_RECEIVER_EMAIL"
PAYPAL_IDENTITY_TOKEN = "PAYPAL_IDENTITY_TOKEN"

# Set l'adresse mail d'Idril

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = '<email>'
EMAIL_HOST_PASSWORD = '???'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# MangoPay

MANGOPAY_CLIENT_ID = "<client_id>"
MANGOPAY_PASSPHRASE = "<Mangopay_passphrase>"
MANGOPAY_BASE_URL = "https://api.sandbox.mangopay.com"
MANGOPAY_DEBUG_MODE = 1
MANGOPAY_PAGE_DEFAULT_STORAGE = True

from django.contrib.auth.models import User
User._meta.get_field_by_name('email')[0]._unique = True

DATE_INPUT_FORMATS = ('%d/%m/%Y','%Y/%m/%d')
