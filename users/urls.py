#coding: utf-8
# Url handlers des utilisateurs
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_detail
from oi.users.models import UserProfile, User

urlpatterns = patterns('oi.users.views',
    (r'^myprofile', 'myprofile'),
    (r'^exportresume', 'exportresume'),
    (r'^profile/(?P<username>\w+)$','userprofile'),
    (r'^dashboard', 'dashboard'),
    (r'^preferences', direct_to_template, {'template': 'users/preferences.html'}),
    (r'^discussions', direct_to_template, {'template': 'users/discussions.html'}),
    (r'^messageswith/(?P<username>\w+)$', 'getusermessages'),
    (r'^createuser$', 'createuser'),
    (r'^resetpassword$', direct_to_template, {'template': 'users/resetpwd.html'}),
    (r'^confirmresetpassword$', 'resetpassword'),
    (r'^changepassword$', direct_to_template, {'template': 'users/changepwd.html'}),
    (r'^confirmchangepassword$', 'changepassword'),
    (r'^invite/(?P<id>\d+)$', 'invite'),
    (r'^writemp/(?P<id>\d+)$', direct_to_template, {'template': 'users/writemp.html'}),
    (r'^sendmp/(?P<id>\d+)$', 'sendMP'),
    (r'^register$', direct_to_template, {'template': 'users/register.html'}),
    (r'^editdetail/(?P<id>\d+)$', 'editdetail'),
    (r'^savedetail/(?P<id>\d+)$', 'savedetail'),
    (r'^deletedetail/(?P<id>\d+)$', 'deletedetail'),    
    (r'^edittitle$', direct_to_template, {'template': 'users/profile/edittitle.html'}),
    (r'^setusertitle$', 'setusertitle'),
    (r'^invoice', 'invoice'),
    (r'^setbirthdate$', 'setbirthdate'),    
    (r'^getpicture/(?P<username>\w+)$', 'getpicture'),    
    (r'^uploadpicture$', 'uploadpicture'),    
)
