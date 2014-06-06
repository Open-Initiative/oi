##coding: utf-8
# Url handlers des projets
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import direct_to_template
from oi.projects.models import Project
from oi.helpers import SPEC_TYPES

urlpatterns = patterns('oi.funding.views',
    (r'^(?P<id>\d+)/$', 'get_project'),
    (r'^(?P<object_id>\d+)/edit$', object_detail, {'template_name': 'funding/project_edit.html', 'queryset': Project.objects.all(), 'extra_context': {'types': SPEC_TYPES}}),
    (r'^bid/(?P<object_id>\d+)$', object_detail, {'template_name': 'funding/dialogue/bid.html','queryset': Project.objects.all()}),
    (r'^(?P<id>\d+)/task$', 'get_feature'),
    (r'^(?P<object_id>\d+)/embed$', object_detail, {'template_name': 'funding/plugin.html','queryset': Project.objects.all()}),
    (r'^(?P<object_id>\d+)/embed_popup$', object_detail, {'template_name': 'funding/tiny_popup.html','queryset': Project.objects.all()}),
    (r'^(?P<id>\d+)/editspec/(?P<specid>\d+)$', 'editspec'),
)
