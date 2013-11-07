#coding: utf-8
# Specific to the funding platform
# Django settings for oi project.
from settings_common import *

REDIRECT_URL = "/funding/"
ROOT_URLCONF = 'oi.urls-funding'
SITE_NAME = "Open Funding"

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
    'compressor',
#    'haystack',
    'oi.messages',
    'oi.projects',
    'oi.funding',
    'oi.users',
    'oi.prjnotify',
    'django.contrib.messages',
) #+ SPECIFIC_INSTALLED_APPS
