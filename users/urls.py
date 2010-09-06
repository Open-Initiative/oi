#coding: utf-8
# Url handlers des utilisateurs
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_detail
from oi.users.models import UserProfile, User

urlpatterns = patterns('oi.users.views',
    (r'^myprofile', 'myprofile'),
    (r'^editprofile$', 'editprofile'),
    (r'^createuser$', 'createuser'),
    (r'^saveprofile$', 'saveprofile'),
    (r'^invite/(?P<id>\d+)$', 'invite'),
    (r'^profile/(?P<username>\w+)$','userprofile'),
    (r'^register$', direct_to_template, {'template': 'users/register.html'}),
    (r'^edittraining/(?P<id>\d+)$', 'edittraining'),
    (r'^editexperience/(?P<id>\d+)$', 'editexperience'),
    (r'^savetraining/(?P<id>\d+)$', 'savetraining'),
    (r'^saveexperience/(?P<id>\d+)$', 'saveexperience'),
)
