#coding: utf-8
# Url handlers des messages
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list
from oi.messages.models import Message

urlpatterns = patterns('oi.messages.views',
    (r'^get/(?P<id>\d+)$', 'getmessage'),
    (r'^getall$', object_list, {'queryset': Message.objects.filter(category=False, public=True).order_by('-created'), 'paginate_by': 10, 'extra_context': {'rfp': False}}),
    (r'^getrfp$', object_list, {'queryset': Message.objects.filter(category=False, public=True, rfp=True).order_by('-created'), 'paginate_by': 10, 'extra_context': {'rfp': True}}),
    (r'^new$', direct_to_template, {'template': "messages/newmessage.html"}),
    (r'^getFile/(?P<filename>\w+\.\w+)$', 'getFile'),
    (r'^edit/(?P<id>\d+)$', 'editmessage'),
    (r'^save/(?P<id>\d+)$', 'savemessage'),
    (r'^vote/(?P<id>\d+)$', 'vote'),
    (r'^hide/(?P<id>\d+)$', 'hidemessage'),
    (r'^share/(?P<id>\d+)/(?P<divid>\w+)$', direct_to_template, {'template': "messages/sharemessage.html"}),
    (r'^confirmshare/(?P<id>\d+)$', 'sharemessage'),
    (r'^move/(?P<id>\d+)/(?P<divid>\w+)$', direct_to_template, {'template': "messages/movemessage.html"}),
    (r'^confirmmove/(?P<id>\d+)$', 'movemessage'),
#    (r'^orphan/(?P<id>\d+)$', 'orphanmessage'),
    (r'^delete/(?P<id>\d+)$', 'deletemessage'),
    (r'^observe/(?P<id>\d+)$', 'observemessage'),
    (r'^uploadForm$', direct_to_template, {'template': "messages/uploadForm.html"}),
    (r'^uploadFile$', 'uploadFile'),
    (r'^listcategories/(?P<id>\d+)$', 'listcategories'),
    (r'^listancestors/(?P<id>\d+)$', 'listancestors'),
    (r'^rss/(?P<id>\d+)$', 'OIFeed'),
)
