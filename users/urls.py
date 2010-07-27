#coding: utf-8
# Url handlers des utilisateurs
from django.conf.urls.defaults import *

urlpatterns = patterns('oi.users.views',
    (r'^myprofile', 'userprofile'),
    (r'^editprofile$', 'editprofile'),
    (r'^saveprofile$', 'saveprofile'),
)