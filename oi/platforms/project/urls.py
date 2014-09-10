##coding: utf-8
# Url handlers des projets
from django.conf.urls import *
from django.template.response import TemplateResponse
from django.views.generic import TemplateView, ListView, DetailView
from oi.projects.models import Project
# Activation de l'admin
from django.contrib import admin
admin.autodiscover()

from random import choice
from string import letters
from django.conf.urls import *
from oi.projects.models import Project, Spec, OINeedsPrjPerms, OI_READ, OI_WRITE

def index(request):
    if request.user.is_authenticated():
        extra_context = {}
        return TemplateResponse(request, "users/dashboard.html", extra_context)
    else:
        return ListView.as_view(queryset=Project.objects.filter(promotedproject__location='index'), template_name='index.html')(request)

urlpatterns = patterns('',
    # Page d'accueil
    (r'^$', index),
    # contenu statique
    (r'^cgu$', TemplateView.as_view(template_name="cgu.html")),    
    (r'^contact$', TemplateView.as_view(template_name="contact.html")),
    (r'^presentation$', TemplateView.as_view(template_name="presentation.html")),
    (r'^presentation-fr$', TemplateView.as_view(template_name="presentation-fr.html")),
    # Pages des messages
    (r'^message/', include('oi.messages.urls')),
    # Pages des projets
    (r'^project/', include('oi.projects.urls')),
    (r'^', include('oi.platforms.project.extend-urls')),
    # Pages des utilisateurs
    (r'^user/', include('oi.users.urls')),
    # notifications
    (r'^notification/', include('oi.prjnotify.urls')),
    # Authentification par defaut
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': "/"}),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Page d'administration
    (r'^admin/', include(admin.site.urls)),
    # Moteur de recherche
#    (r'^search/', oi_search_view_factory()),
    # Js translation
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog',),
    (r'^i18n/', include('django.conf.urls.i18n')),
    )
