#coding: utf-8
# Url handlers des messages
from django.conf.urls.defaults import *

urlpatterns = patterns('oi.messages.views',
    (r'^edit/(?P<id>\d+)$', 'editmessage'),
    (r'^get/(?P<id>\d+)$', 'getmessage'),
    (r'^save/(?P<id>\d+)$', 'savemessage'),
    (r'^vote/(?P<id>\d+)$', 'vote'),
    (r'^delete/(?P<id>\d+)$', 'deletemessage'),
    (r'^listcategories/(?P<id>\d+)$', 'listcategories'),
)
