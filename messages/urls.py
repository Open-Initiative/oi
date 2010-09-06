#coding: utf-8
# Url handlers des messages
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('oi.messages.views',
    (r'^new$', 'newmessage'),
    (r'^uploadForm$', direct_to_template, {'template': "messages/uploadForm.html"}),
    (r'^uploadFile$', 'uploadFile'),
    (r'^getFile/(?P<filename>\w+\.\w+)$', 'getFile'),
    (r'^edit/(?P<id>\d+)$', 'editmessage'),
    (r'^edit/(?P<id>\d+)$', 'editmessage'),
    (r'^get/(?P<id>\d+)$', 'getmessage'),
    (r'^getall$', 'getmessages'),
    (r'^save/(?P<id>\d+)$', 'savemessage'),
    (r'^vote/(?P<id>\d+)$', 'vote'),
    (r'^delete/(?P<id>\d+)$', 'deletemessage'),
    (r'^listcategories/(?P<id>\d+)$', 'listcategories'),
)
