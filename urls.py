from django.conf.urls.defaults import *
from haystack.views import SearchView
from haystack.query import SearchQuerySet
# Activation de l'admin
from django.contrib import admin
admin.autodiscover()

def oi_search_view_factory(view_class=SearchView, *args, **kwargs):
    def search_view(request):
        return view_class(searchqueryset=SearchQuerySet().filter(public=True).filter_or(perms=request.user) , *args, **kwargs)(request)
    return search_view

urlpatterns = patterns('',
    # Page d'accueil
    (r'^$', 'oi.messages.views.index'),
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
    # Moteur de recherche
    (r'^search/', oi_search_view_factory()),
    # notifications
    (r'^notification/', include('notification.urls')),
    )
