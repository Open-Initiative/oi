#coding: utf-8
# Url handlers des projets
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import direct_to_template
from oi.projects.models import Project, OINeedsPrjPerms, OI_READ, OI_WRITE

urlpatterns = patterns('oi.projects.views',
    (r'^get/(?P<object_id>\d+)$', object_detail, {'queryset': Project.objects.all()}),
    (r'^gettask/(?P<object_id>\d+)$', object_detail,{'template_name': 'projects/task.html','queryset': Project.objects.all(),'template_object_name':"task"}),
    (r'^getall$', 'getprojects'),
    (r'^edit/(?P<id>\d+)$', 'editproject'),
    (r'^save/(?P<id>\d+)$', 'saveproject'),
    (r'^bid/(?P<id>\d+)$', 'bidproject'),
    (r'^start/(?P<id>\d+)$', 'startproject'),
    (r'^deliver/(?P<id>\d+)$', 'deliverproject'),
    (r'^validate/(?P<id>\d+)$', 'validateproject'),
    (r'^eval/(?P<id>\d+)$', direct_to_template, {'template': 'projects/evalproject.html'}),
    (r'^confirmeval/(?P<id>\d+)$', 'evaluateproject'),
    (r'^delete/(?P<id>\d+)$', 'deleteproject'),
    (r'^summary/(?P<id>\d+)$', 'projectview'),
    (r'^hide/(?P<id>\d+)$', 'hideproject'),
    (r'^share/(?P<id>\d+)/(?P<divid>\w+)$', direct_to_template, {'template': "projects/shareproject.html"}),
    (r'^confirmshare/(?P<id>\d+)$', 'shareproject'),
    (r'^(?P<id>\d+)/editspec/(?P<specid>\d+)$', 'editspec'),
    (r'^(?P<id>\d+)/editspecdetails/(?P<specid>\d+)$', 'editspecdetails'),
    (r'^(?P<id>\d+)/uploadfile/(?P<specid>\d+)$', 'uploadfile'),
    (r'^(?P<id>\d+)/savespec/(?P<specid>\d+)$', 'savespec'),
    (r'^(?P<id>\d+)/deletespec/(?P<specid>\d+)$', 'deletespec'),
    (r'^(?P<id>\d+)/deltmp$', 'deltmpfile'),
    (r'^(?P<id>\d+)/(?P<filename>.+)$', 'getfile'),
)
