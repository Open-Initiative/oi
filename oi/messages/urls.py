#coding: utf-8
# Url handlers des messages
from django.conf.urls import *
from django.views.generic import TemplateView, ListView
#from django.views.generic.list_detail import object_list
from oi.messages.models import Message

urlpatterns = patterns('oi.messages.views',
    (r'^get/(?P<id>\d+)$', 'getmessage'),
    (r'^ldpcontainermessage/(?P<id>\d+)$', 'messagetojsonld'),
    (r'^new$', TemplateView.as_view(template_name="messages/newmessage.html")),
    (r'^getFile/(?P<filename>.+)$', 'getFile'),
    (r'^edit/(?P<id>\d+)$', 'editmessage'),
    (r'^save/(?P<id>\d+)$', 'savemessage'),
    (r'^vote/(?P<id>\d+)$', 'vote'),
    (r'^move/(?P<id>\d+)/(?P<divid>\w+)$', TemplateView.as_view(template_name="messages/movemessage.html")),
    (r'^confirmmove/(?P<id>\d+)$', 'movemessage'),
    (r'^delete/(?P<id>\d+)$', 'deletemessage'),
    (r'^uploadForm$', TemplateView.as_view(template_name="messages/uploadForm.html")),
    (r'^uploadFile$', 'uploadFile'),
    (r'^listancestors/(?P<id>\d+)$', 'listancestors'),
    (r'^rss/(?P<id>\d+)$', 'OIFeed'),
)
