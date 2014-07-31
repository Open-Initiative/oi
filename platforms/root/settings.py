#coding: utf-8
# Settings for the main platform
# Django settings for oi project.
from oi.settings_common import *

REDIRECT_URL = ""
ROOT_URLCONF = 'oi.platforms.root.urls'
SITE_NAME = "Open Initiative"

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    HOME_DIR + "/oi/platforms/root/templates/", 
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
    'oi.users',
    'oi.prjnotify',
    'django.contrib.messages',
)+ SPECIFIC_INSTALLED_APPS
