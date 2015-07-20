import os,sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'protodjango.settings'
sys.path.append('/home/lamp')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
