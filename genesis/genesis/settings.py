"""
Django settings for genesis project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import re
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3ppc!k=ybs7av5ci*stn^_@$5=t$nh765gb4ag(7#pz7y@=!c6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '*']

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

# Application definition

INSTALLED_APPS = [
    # 'dal',
    # 'dal_select2',
    # 'autotranslate',
    # 'grappelli_menu',
    'django.contrib.contenttypes',
    'grappelli',
    # 'grappelli.dashboard',
    'grappelli_autocomplete_fk_edit_link',
    # 'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',

    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'lab',
    'com',
    'django.contrib.humanize',
    'django_ace',
    # 'dbtemplates',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # 'LOCATION': 's_unique-snowflake',
    },
    # 'default': {
    #     'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    # }

}

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]
ROOT_URLCONF = 'genesis.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [
#             os.path.join(BASE_DIR, 'templates')
#         ],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
SITE_ID = 1
TEMPLATES = [
  {
      'BACKEND': 'django.template.backends.django.DjangoTemplates',
      'DIRS': [ # your template dirs here
          os.path.join(BASE_DIR, 'templates'),
      ],
      'APP_DIRS': False,
      'OPTIONS': {
          'context_processors': [
              'django.contrib.auth.context_processors.auth',
              'django.template.context_processors.debug',
              'django.template.context_processors.i18n',
              'django.template.context_processors.media',
              'django.template.context_processors.static',
              'django.template.context_processors.tz',
              'django.contrib.messages.context_processors.messages',
              'django.template.context_processors.request',
          ],
          'loaders': [
              'django.template.loaders.filesystem.Loader',
              'django.template.loaders.app_directories.Loader',
              # 'dbtemplates.loader.Loader',

          ],
      },
  },
]

WSGI_APPLICATION = 'genesis.wsgi.application'



# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'genesis',
        'PASSWORD': 'gsis',
        'USER': 'evren',
        # 'HOST': 'localhost'
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/
USE_THOUSAND_SEPARATOR = True

LANGUAGE_CODE = 'tr'
# LANGUAGE_CODE = 'en-EN'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

# GRAPPELLI_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
GRAPPELLI_ADMIN_TITLE = 'GENESIS'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

try:
    from .local_settings import *
except ImportError:
    pass


STATIC_ROOT = os.path.join(BASE_DIR, "static_serve/")

DEFAULT_CACHE_EXPIRE_TIME = 30


IGNORABLE_404_URLS = [
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon\.ico$'),
    re.compile(r'^/robots\.txt$'),
]
