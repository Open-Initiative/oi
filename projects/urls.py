#coding: utf-8
# Url handlers des projets
from django.conf.urls.defaults import *

urlpatterns = patterns('oi.projects.views',
    (r'^edit/(?P<id>\d+)$', 'editproject'),
    (r'^get/(?P<id>\d+)$', 'getproject'),
    (r'^save/(?P<id>\d+)$', 'saveproject'),
    (r'^delete/(?P<id>\d+)$', 'deleteproject'),
    (r'^(?P<projectid>\d+)/editspec/(?P<specid>\d+)$', 'editspec'),
    (r'^(?P<projectid>\d+)/editspecdetails/(?P<specid>\d+)$', 'editspecdetails'),
    (r'^(?P<projectid>\d+)/uploadfile/(?P<specid>\d+)$', 'uploadfile'),
    (r'^(?P<projectid>\d+)/savespec/(?P<specid>\d+)$', 'savespec'),
    (r'^(?P<projectid>\d+)/deletespec/(?P<specid>\d+)$', 'deletespec'),
    (r'^getfile/(?P<filename>.+)$', 'getfile'),
)