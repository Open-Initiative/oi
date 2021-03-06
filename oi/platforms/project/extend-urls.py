##coding: utf-8
# Url handlers des projets
from random import choice
from string import letters
from django.conf.urls import *
from django.views.generic import TemplateView, DetailView
from oi.projects.models import Project, Spec, OINeedsPrjPerms, OI_READ, OI_WRITE

urlpatterns = patterns('oi.platforms.project.views',
    (r'^(?P<id>\d+)/$', 'getproject'),
    (r'^(?P<id>\d+)/view/(?P<view>\w*)$', 'getproject'),
    (r'^get/(?P<id>\d+)/(?P<view>\w*)$', 'getproject'),
    (r'^get/(?P<id>\d+)/view/(?P<view>\w*)$', 'getproject'),
    (r'^(?P<pk>\d+)/summarize$', DetailView.as_view(model=Project, template_name='projects/project_sum.html', context_object_name='Project.objects.all()')),
    (r'^edit/(?P<id>\d+)$', 'editproject'),
    (r'^edittitle/(?P<object_id>\d+)$', DetailView.as_view(template_name='projects/dialogue/edittitle.html',queryset=' Project.objects.all()')),
    (r'^(?P<object_id>\d+)/export$', DetailView.as_view(template_name="projects/export/export.html",queryset='Project.objects.all()')),
    (r'^(?P<id>\d+)/editspec/(?P<specid>\d+)$', 'editspec'),
    (r'^(?P<id>\d+)/editspecdetails/(?P<specid>\d+)$', 'editspecdetails'),
    (r'^rss/(?P<id>\d+)$', 'OIFeed'),
#    (r'^', include('oi.platforms.project.urls')),
)
