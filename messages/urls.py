#coding: utf-8
# Url handlers des messages
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list
from oi.messages.models import Message

urlpatterns = patterns('oi.messages.views',
    (r'^get/(?P<id>\d+)$', 'getmessage'),
    (r'^new$', direct_to_template, {'template': "messages/newmessage.html"}),
    (r'^getFile/(?P<filename>\w+\.\w+)$', 'getFile'),
    (r'^edit/(?P<id>\d+)$', 'editmessage'),
    (r'^save/(?P<id>\d+)$', 'savemessage'),
    (r'^vote/(?P<id>\d+)$', 'vote'),
    (r'^move/(?P<id>\d+)/(?P<divid>\w+)$', direct_to_template, {'template': "messages/movemessage.html"}),
    (r'^confirmmove/(?P<id>\d+)$', 'movemessage'),
    (r'^delete/(?P<id>\d+)$', 'deletemessage'),
    (r'^uploadForm$', direct_to_template, {'template': "messages/uploadForm.html"}),
    (r'^uploadFile$', 'uploadFile'),
    (r'^listancestors/(?P<id>\d+)$', 'listancestors'),
    (r'^rss/(?P<id>\d+)$', 'OIFeed'),
)
