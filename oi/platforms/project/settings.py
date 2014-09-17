#coding: utf-8
# Settings for the main platform
# Django settings for oi project.
from oi.settings_common import *

REDIRECT_URL = "/prjmgt/"
ROOT_URLCONF = 'oi.platforms.project.urls'
SITE_NAME = "Open Initiative Projects"

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    HOME_DIR + "/oi/oi/platforms/project/templates/",
    "/oi/oi/messages/templates/",
    "/oi/oi/prjnotify/templates/",
    "/oi/oi/users/templates/", 
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
    'oi.platforms.project',
    'oi.users',
    'oi.prjnotify',
    'django.contrib.messages',
)+ SPECIFIC_INSTALLED_APPS
