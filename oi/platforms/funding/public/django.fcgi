#!/usr/bin/python2
import os, sys

_PROJECT_NAME = "oi"
_PLATFORM_NAME = "funding"

_PLATFORM_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(_PLATFORM_DIR)))
_MODULES_DIR = "%s/%s"%(os.path.dirname(_PROJECT_DIR), "modules")

sys.path.insert(0, _PLATFORM_DIR)
sys.path.insert(0, _PROJECT_DIR)
sys.path.insert(0, _MODULES_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = "%s.platforms.%s.settings"%(_PROJECT_NAME, _PLATFORM_NAME)
from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
