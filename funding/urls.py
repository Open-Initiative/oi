##coding: utf-8
# Url handlers des projets
from django.conf.urls import *
#from django.views.generic.list_detail import object_detail
from django.views.generic import TemplateView, DetailView
from oi.projects.models import Project

urlpatterns = patterns('oi.funding.views',
    (r'^(?P<id>\d+)/$', 'get_project'),
    (r'^(?P<object_id>\d+)/edit$', DetailView.as_view(template_name='funding/project_edit.html', queryset='Project.objects.all()')),
    (r'^bid/(?P<object_id>\d+)$', DetailView.as_view(template_name='funding/dialogue/bid.html',queryset='Project.objects.all()')),
    (r'^(?P<id>\d+)/task$', 'get_feature'),
    (r'^(?P<object_id>\d+)/embed$', DetailView.as_view(template_name='funding/plugin.html',queryset='Project.objects.all()')),
    (r'^(?P<object_id>\d+)/embed_popup$', DetailView.as_view(template_name='funding/tiny_popup.html',queryset='Project.objects.all()')),
    (r'^(?P<id>\d+)/editspec/(?P<specid>\d+)$', 'editspec'),
)
