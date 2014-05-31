from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic import ListView
from oi.projects.models import Project
# Activation de l'admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Page d'accueil
    (r'^$', ListView.as_view(queryset=Project.objects.filter(promotedproject__location='fundingindex'), template_name='funding/index.html')),
    #OpenTheWorld page
    (r'^opentheworld$', ListView.as_view(queryset=Project.objects.filter(promotedproject__location='otw1'), template_name='funding/opentheworld.html')),
    (r'^opentheworld$', direct_to_template, {'template': "funding/opentheworld.html"}),
    # contenu statique
    (r'^cgu$', direct_to_template, {'template': "cgu.html"}),    
    (r'^contact$', direct_to_template, {'template': "contact.html"}),
    (r'^presentation$', direct_to_template, {'template': "funding/presentation.html"}),
    # Pages des messages
    (r'^message/', include('oi.messages.urls')),
    (r'^funding/', include('oi.funding.urls')),
    # Pages des projets
    (r'^project/', include('oi.projects.urls_api')),
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
