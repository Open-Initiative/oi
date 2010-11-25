import os,sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'oi.settings'
sys.path.append('/home/oi')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
