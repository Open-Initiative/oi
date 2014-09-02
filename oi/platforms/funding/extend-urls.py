##coding: utf-8
# Url handlers des projets
from django.conf.urls import *
from django.views.generic import TemplateView, DetailView
from oi.projects.models import Project
from oi.helpers import SPEC_TYPES

urlpatterns = patterns('oi.platforms.funding.views',
    (r'^(?P<id>\d+)/$', 'get_project'),
    (r'^(?P<pk>\d+)/edit$', DetailView.as_view(model=Project, template_name='funding/project_edit.html', context_object_name='Project.objects.all()')),
    (r'^bid/(?P<object_id>\d+)$', DetailView.as_view(template_name='funding/dialogue/bid.html',queryset='Project.objects.all()')),
    (r'^(?P<id>\d+)/task$', 'get_feature'),
    (r'^(?P<pk>\d+)/embed$', DetailView.as_view(model=Project, template_name='funding/plugin.html',context_object_name='Project.objects.all()')),
    (r'^(?P<pk>\d+)/embed_popup$', DetailView.as_view(model=Project, template_name='funding/tiny_popup.html',context_object_name='Project.objects.all()')),
    (r'^(?P<id>\d+)/editspec/(?P<specid>\d+)$', 'editspec'),
#    (r'^', include('oi.platforms.funding.urls')),
)
