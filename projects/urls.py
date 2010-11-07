#coding: utf-8
# Url handlers des projets
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_detail
from oi.projects.models import Project, OINeedsPrjPerms, OI_READ, OI_WRITE

urlpatterns = patterns('oi.projects.views',
    (r'^get/(?P<object_id>\d+)$', object_detail, {'queryset': Project.objects.all()}),
    (r'^gettask/(?P<object_id>\d+)$', object_detail,{'template_name': 'projects/task.html','queryset': Project.objects.all(),'template_object_name':"task"}),
    (r'^edit/(?P<id>\d+)$', 'editproject'),
    (r'^save/(?P<id>\d+)$', 'saveproject'),
    (r'^delete/(?P<id>\d+)$', 'deleteproject'),
    (r'^finish/(?P<id>\d+)$', 'finishproject'),
    (r'^summary/(?P<id>\d+)$', 'projectview'),
    (r'^(?P<id>\d+)/editspec/(?P<specid>\d+)$', 'editspec'),
    (r'^(?P<id>\d+)/editspecdetails/(?P<specid>\d+)$', 'editspecdetails'),
    (r'^(?P<id>\d+)/uploadfile/(?P<specid>\d+)$', 'uploadfile'),
    (r'^(?P<id>\d+)/savespec/(?P<specid>\d+)$', 'savespec'),
    (r'^(?P<id>\d+)/deletespec/(?P<specid>\d+)$', 'deletespec'),
    (r'^(?P<id>\d+)/deltmp$', 'deltmpfile'),
    (r'^(?P<id>\d+)/(?P<filename>.+)$', 'getfile'),
)
