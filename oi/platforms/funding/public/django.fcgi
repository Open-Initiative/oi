#!/usr/bin/python2
import os, sys

_PROJECT_NAME = "oi"
_PLATFORM_NAME = "funding"

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROJECT_DIR = "%s/%s"%(_ROOT_DIR, _PROJECT_NAME)
_PLATFORM_DIR = "%s/%s/platforms/%s"%(_PROJECT_DIR, _PROJECT_NAME, _PLATFORM_NAME)
_MODULES_DIR = "%s/%s"%(_ROOT_DIR, "modules")

sys.path.insert(0, _PLATFORM_DIR)
sys.path.insert(0, _PROJECT_DIR)
sys.path.insert(0, _MODULES_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = "%s.platforms.%s.settings"%(_PROJECT_NAME, _PLATFORM_NAME)
from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
