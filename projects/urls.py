##coding: utf-8
# Url handlers des projets
from random import choice
from string import letters
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import direct_to_template
from oi.projects.models import Project, Spec, OINeedsPrjPerms, OI_READ, OI_WRITE
from oi.helpers import SPEC_TYPES

urlpatterns = patterns('oi.projects.views',
    (r'^(?P<id>\d+)/$', 'getproject'),
    (r'^(?P<id>\d+)/view/(?P<view>\w*)$', 'getproject'),
    (r'^get/(?P<id>\d+)/(?P<view>\w*)$', 'getproject'),
    (r'^get/(?P<id>\d+)/view/(?P<view>\w*)$', 'getproject'),
    (r'^(?P<object_id>\d+)/summarize$', object_detail, {'template_name': 'projects/project_sum.html', 'queryset': Project.objects.all(), 'extra_context': {'types': SPEC_TYPES}}),
    (r'^edit/(?P<id>\d+)$', 'editproject'),
    (r'^edittitle/(?P<object_id>\d+)$', object_detail, {'template_name': 'projects/dialogue/edittitle.html','queryset': Project.objects.all()}),
    (r'^offer/(?P<object_id>\d+)$', object_detail, {'template_name': 'projects/dialogue/offer.html','queryset': Project.objects.all()}),
    (r'^delegate/(?P<id>\d+)$', direct_to_template, {'template': 'projects/dialogue/delegate.html'}),
    (r'^bid/(?P<object_id>\d+)$', object_detail, {'template_name': 'projects/dialogue/bid.html','queryset': Project.objects.all()}),
    (r'^validator/(?P<object_id>\d+)$', object_detail, {'template_name': 'projects/dialogue/validator.html','queryset': Project.objects.all()}),
    (r'^eval/(?P<id>\d+)$', direct_to_template, {'template': 'projects/dialogue/eval.html'}),
    (r'^(?P<id>\d+)/share$', direct_to_template, {'template': "projects/dialogue/share.html"}),
    (r'^(?P<object_id>\d+)/export$', object_detail, {'template_name': "projects/export/export.html",'queryset': Project.objects.all()}),
    (r'^(?P<id>\d+)/editspec/(?P<specid>\d+)$', 'editspec'),
    (r'^(?P<id>\d+)/editspecdetails/(?P<specid>\d+)$', 'editspecdetails'),
    (r'^rss/(?P<id>\d+)$', 'OIFeed'),
    (r'^', include('oi.projects.urls_api')),
)
