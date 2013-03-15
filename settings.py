#coding: utf-8
# Settings for the main platform
# Django settings for oi project.
from settings_common import *

ROOT_URLCONF = 'oi.urls'
SITE_NAME = "Open Initiative"

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    HOME_DIR + "/oi/templates/"
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'registration',
    'south',
    'corsheaders',
#    'haystack',
    'oi.messages',
    'oi.projects',
    'oi.users',
    'oi.prjnotify',
    'django.contrib.messages',
)
