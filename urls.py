from django.conf.urls.defaults import *
# Activation de l'admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Page d'accueil
    (r'^$', 'oi.messages.views.getmessages'),
    # Pages des messages
    (r'^message/', include('oi.messages.urls')),
    # Pages des projets
    (r'^project/', include('oi.projects.urls')),
    # Pages des utilisateurs
    (r'^user/', include('oi.users.urls')),
    # Authentification par defaut
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Page d'administration
    (r'^admin/', include(admin.site.urls)),
    )
