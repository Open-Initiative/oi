from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic import ListView
from haystack.views import SearchView
from haystack.query import SearchQuerySet
from oi.messages.models import Message
# Activation de l'admin
from django.contrib import admin
admin.autodiscover()

def oi_search_view_factory(view_class=SearchView, *args, **kwargs):
    def search_view(request):
        return view_class(searchqueryset=SearchQuerySet().filter(public=True).filter_or(perms=request.user) , *args, **kwargs)(request)
    return search_view

urlpatterns = patterns('',
    # Page d'accueil
    (r'^$',  ListView.as_view(queryset=Message.objects.filter(promotedmessage__location='index'), template_name='index.html')),
    (r'^index/(?P<id>\d+)$', direct_to_template, {'template': "index.html"}),
    # contenu statique
    (r'^cgu$', direct_to_template, {'template': "cgu.html"}),    
    (r'^contact$', direct_to_template, {'template': "contact.html"}),
    (r'^presentation$', direct_to_template, {'template': "presentation.html"}),
    # Pages des messages
    (r'^message/', include('oi.messages.urls')),
    # Pages des projets
    (r'^project/', include('oi.projects.urls')),
    # Pages des utilisateurs
    (r'^user/', include('oi.users.urls')),
    # notifications
    (r'^notification/', include('oi.notification.urls')),
    # Authentification par defaut
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': "/"}),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Page d'administration
    (r'^admin/', include(admin.site.urls)),
    # Moteur de recherche
    (r'^search/', oi_search_view_factory()),
    # Js translation
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog',),
    (r'^i18n/', include('django.conf.urls.i18n')),
    )
