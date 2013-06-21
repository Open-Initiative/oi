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
    (r'^(?P<id>\d+)/listtasks$', 'listtasks'),
    (r'^(?P<id>\d+)/addrelease$', 'addrelease'),
    (r'^(?P<id>\d+)/changerelease$', 'changerelease'),
    (r'^(?P<id>\d+)/assignrelease$', 'assignrelease'),
    (r'^save/(?P<id>\d+)$', 'saveproject'),
    (r'^editdate/(?P<id>\d+)$', 'editdate'),
    (r'^setpriority/(?P<id>\d+)$', 'setpriority'),
    (r'^(?P<id>\d+)/sort$', 'sorttasks'),
    (r'^confirmedittitle/(?P<id>\d+)$', 'edittitle'),    
    (r'^confirmoffer/(?P<id>\d+)$', 'offerproject'),
    (r'^confirmdelegate/(?P<id>\d+)$', 'delegateproject'),
    (r'^confirmbid/(?P<id>\d+)$', 'bidproject'),
    (r'^confirmvalidator/(?P<id>\d+)$', 'validatorproject'),
    (r'^start/(?P<id>\d+)$', 'startproject'),
    (r'^deliver/(?P<id>\d+)$', 'deliverproject'),
    (r'^validate/(?P<id>\d+)$', 'validateproject'),
    (r'^confirmeval/(?P<id>\d+)$', 'evaluateproject'),
    (r'^cancelbid/(?P<id>\d+)$', 'cancelbid'),
    (r'^answerdelegate/(?P<id>\d+)$', 'answerdelegate'),
    (r'^answerdelay/(?P<id>\d+)$', 'answerdelay'),
    (r'^answercancelbid/(?P<id>\d+)$', 'answercancelbid'),
    (r'^cancel/(?P<id>\d+)$', 'cancelproject'),
    (r'^answercancelproject/(?P<id>\d+)$', 'answercancelproject'),
    (r'^delete/(?P<id>\d+)$', 'deleteproject'),
    (r'^move/(?P<id>\d+)$', 'moveproject'), 
    (r'^(?P<id>\d+)/addrequirement$', 'addrequirement'),
    (r'^(?P<id>\d+)/removerequirement$', 'removerequirement'),
    (r'^(?P<id>\d+)/setpublic$', 'setpublicproject'),
    (r'^(?P<id>\d+)/confirmshare$', 'shareproject'),
    (r'^editprogress/(?P<id>\d+)$', 'editprogress'),
    (r'^(?P<id>\d+)/setgihubtoken$', 'setgihubtoken'),
    (r'^(?P<id>\d+)/getgithubrepos$', 'getgithubrepos'),
    (r'^(?P<id>\d+)/setgithubsync$', 'setgithubsync'),
    (r'^(?P<id>\d+)/syncgithub$', 'syncgithub'),
    (r'^(?P<id>\d+)/togglegithubhook$', 'togglegithubhook'),
    (r'^(?P<id>\d+)/createtask$', 'createtask'),
    (r'^(?P<id>\d+)/fav$', 'favproject'),
    (r'^(?P<id>\d+)/uploadfile/(?P<specid>\d+)$', 'uploadfile'),
    (r'^(?P<id>\d+)/savespec/(?P<specid>\d+)$', 'savespec'),
    (r'^(?P<id>\d+)/movespec/(?P<specid>\d+)$', 'movespec'),
    (r'^(?P<id>\d+)/deletespec/(?P<specid>\d+)$', 'deletespec'),
    (r'^(?P<id>\d+)/removespot/(?P<specid>\d+)/(?P<spotid>\d+)$', 'removeSpot'),
    (r'^(?P<id>\d+)/savespot/(?P<specid>\d+)/(?P<spotid>\d+)$', 'savespot'),
    (r'^(?P<id>\d+)/deltmp$', 'deltmpfile'),
    (r'^(?P<id>\d+)/(?P<filename>.+)$', 'getfile'),
)
