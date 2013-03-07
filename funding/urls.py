##coding: utf-8
# Url handlers des projets
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import direct_to_template
from oi.projects.models import Project
from oi.helpers import SPEC_TYPES

urlpatterns = patterns('oi.funding.views',
    (r'^(?P<object_id>\d+)/$', object_detail, {'template_name': 'funding/project_detail.html', 'queryset': Project.objects.all(), 'extra_context': {'types': SPEC_TYPES}}),
    (r'^(?P<object_id>\d+)/edit$', object_detail, {'template_name': 'funding/edit_project.html', 'queryset': Project.objects.all(), 'extra_context': {'types': SPEC_TYPES}}),
    (r'^(?P<id>\d+)/task$', 'get_feature'),
    (r'^(?P<id>\d+)/editspec/(?P<specid>\d+)$', 'editspec'),
)
