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
    (r'^listtasks/(?P<id>\d+)$', 'listtasks'),
#    (r'^getall$', 'getprojects'),
    (r'^edit/(?P<id>\d+)$', 'editproject'),
    (r'^save/(?P<id>\d+)$', 'saveproject'),
    (r'^editdate/(?P<id>\d+)$', 'editdate'),
    (r'^setpriority/(?P<id>\d+)$', 'setpriority'),
    (r'^edittitle/(?P<object_id>\d+)$', object_detail, {'template_name': 'projects/dialogue/edittitle.html','queryset': Project.objects.all()}),
    (r'^confirmedittitle/(?P<id>\d+)$', 'edittitle'),    
    (r'^offer/(?P<object_id>\d+)$', object_detail, {'template_name': 'projects/dialogue/offer.html','queryset': Project.objects.all()}),
    (r'^confirmoffer/(?P<id>\d+)$', 'offerproject'),
    (r'^delegate/(?P<id>\d+)$', direct_to_template, {'template': 'projects/dialogue/delegate.html'}),
    (r'^confirmdelegate/(?P<id>\d+)$', 'delegateproject'),
    (r'^bid/(?P<object_id>\d+)$', object_detail, {'template_name': 'projects/dialogue/bid.html','queryset': Project.objects.all()}),
    (r'^confirmbid/(?P<id>\d+)$', 'bidproject'),
    (r'^start/(?P<id>\d+)$', 'startproject'),
    (r'^deliver/(?P<id>\d+)$', 'deliverproject'),
    (r'^validate/(?P<id>\d+)$', 'validateproject'),
    (r'^eval/(?P<id>\d+)$', direct_to_template, {'template': 'projects/dialogue/eval.html'}),
    (r'^confirmeval/(?P<id>\d+)$', 'evaluateproject'),
    (r'^cancelbid/(?P<id>\d+)$', 'cancelbid'),
    (r'^answerdelegate/(?P<id>\d+)$', 'answerdelegate'),
    (r'^answerdelay/(?P<id>\d+)$', 'answerdelay'),
    (r'^answercancelbid/(?P<id>\d+)$', 'answercancelbid'),
    (r'^cancel/(?P<id>\d+)$', 'cancelproject'),
    (r'^answercancelproject/(?P<id>\d+)$', 'answercancelproject'),
    (r'^delete/(?P<id>\d+)$', 'deleteproject'),
    (r'^move/(?P<id>\d+)$', 'moveproject'),    
    (r'^togglehide/(?P<id>\d+)$', 'togglehideproject'),
    (r'^share/(?P<id>\d+)/(?P<divid>\w+)$', direct_to_template, {'template': "projects/dialogue/share.html"}),
    (r'^confirmshare/(?P<id>\d+)$', 'shareproject'),
    (r'^editprogress/(?P<id>\d+)$', 'editprogress'),
    (r'^(?P<id>\d+)/fav$', 'favproject'),
    (r'^(?P<id>\d+)/editspec/(?P<specid>\d+)$', 'editspec'),
    (r'^(?P<id>\d+)/editspecdetails/(?P<specid>\d+)$', 'editspecdetails'),
    (r'^(?P<id>\d+)/uploadfile/(?P<specid>\d+)$', 'uploadfile'),
    (r'^(?P<id>\d+)/savespec/(?P<specid>\d+)$', 'savespec'),
    (r'^(?P<id>\d+)/deletespec/(?P<specid>\d+)$', 'deletespec'),
    (r'^(?P<id>\d+)/removespot/(?P<specid>\d+)/(?P<spotid>\d+)$', 'removeSpot'),
    (r'^(?P<id>\d+)/savespot/(?P<specid>\d+)/(?P<spotid>\d+)$', 'savespot'),
    (r'^(?P<id>\d+)/deltmp$', 'deltmpfile'),
    (r'^(?P<id>\d+)/(?P<filename>.+)$', 'getfile'),
    (r'^rss/(?P<id>\d+)$', 'OIFeed'),
)
