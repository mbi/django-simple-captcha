# -*- coding: utf-8 -*-
import django
import os
import sys
from six import u

SITE_ID = 1

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

PYTHON_VERSION = '%s.%s' % sys.version_info[:2]
DJANGO_VERSION = django.get_version()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'django-simple-captcha.db')
    }
}

TEST_DATABASE_CHARSET = "utf8"
TEST_DATABASE_COLLATION = "utf8_general_ci"

DATABASE_SUPPORTS_TRANSACTIONS = True

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'captcha',
]

LANGUAGE_CODE = "en"

LANGUAGES = (
    ('en', 'English'),
    ('ja', u('日本語')),
)

FIXTURE_DIRS = (
    os.path.join(PROJECT_PATH, 'fixtures'),
)

ROOT_URLCONF = 'testproject.urls'

DEBUG = True
TEMPLATE_DEBUG = True
TEMPLATE_DIRS = ('templates',)

# Django 1.4 TZ support
USE_TZ = True
SECRET_KEY = 'empty'

MIDDLEWARE_CLASSES = ()

CAPTCHA_FLITE_PATH = os.environ.get('CAPTCHA_FLITE_PATH', None)
CAPTCHA_BACKGROUND_COLOR = 'transparent'
# CAPTCHA_BACKGROUND_COLOR = '#ffffffff'
