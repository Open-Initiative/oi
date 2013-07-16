#coding: utf-8
# Url handlers des utilisateurs
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_detail, object_list
from oi.messages.models import Message
from oi.users.models import UserProfile, User

urlpatterns = patterns('oi.users.views',
    (r'^myprofile', 'myprofile'),
    (r'^exportresume/(?P<username>[\w\-\.]+)$', 'exportresume'),
    (r'^profile/(?P<username>[\w\-\.]+)$','userprofile'),
    (r'^dashboard', login_required(direct_to_template), {'template': "users/dashboard.html"}),
    (r'^myblog', login_required(direct_to_template), {'template': "users/blog.html"}),
    (r'^blog/(?P<object_id>\d+)$', object_detail,{'template_name': 'users/blog.html','queryset': User.objects.all(),'template_object_name':"selected_user"}),
    (r'^paymenthistory', login_required(direct_to_template), {'template': "users/paymenthistory.html"}),
    (r'^confirmpayment', 'myaccount'),
    (r'^updatepayment', 'updatepayment'),
    (r'^myaccount', 'myaccount'),
    (r'^setemailing', 'setemailing'),
    (r'^savecontactinfo', 'savecontactinfo'),
    (r'^savename', 'savename'),
    (r'^setrss', 'setrss'),    
    (r'^discussions', direct_to_template, {'template': 'users/discussions.html'}),
    (r'^messageswith/(?P<username>[\w\-\.]+)$', 'getusermessages'),
    (r'^createuser$', 'createuser'),
    (r'^resetpassword$', direct_to_template, {'template': 'users/resetpwd.html'}),
    (r'^confirmresetpassword$', 'resetpassword'),
    (r'^changepassword$', direct_to_template, {'template': 'users/changepwd.html'}),
    (r'^confirmchangepassword$', 'changepassword'),
    (r'^changeemail$', direct_to_template, {'template': 'users/changeemail.html'}),
    (r'^confirmchangeemail$', 'changeemail'),
    (r'^savebio$', 'savebio'),
    (r'^invite/(?P<username>[\w\-\.]+)$', 'invite'),
    (r'^writemp/(?P<username>[\w\-\.]+)$', direct_to_template, {'template': 'users/writemp.html'}),
    (r'^sendmp/(?P<username>[\w\-\.]+)$', 'sendMP'),
    (r'^archivenotice$', 'archivenotice'),
    (r'^register$', direct_to_template, {'template': 'users/register.html'}),
    (r'^editdetail/(?P<id>\d+)$', 'editdetail'),
    (r'^savedetail/(?P<id>\d+)$', 'savedetail'),
    (r'^deletedetail/(?P<id>\d+)$', 'deletedetail'),    
    (r'^edittitle$', login_required(direct_to_template), {'template': 'users/profile/edittitle.html'}),
    (r'^settitle$', 'settitle'),
    (r'^settaxrate$', 'settaxrate'),
    (r'^selectnamedisplay$', 'listnamedisplays'),
    (r'^setnamedisplay$', 'setnamedisplay'),
    (r'^invoice', 'invoice'),
    (r'^setbirthdate$', 'setbirthdate'),    
    (r'^getpicture/(?P<username>[\w\-\.]*)$', 'getpicture'),    
    (r'^uploadpicture$', 'uploadpicture'),
    (r'^accounts/', include('registration.backends.default.urls')),    
)
