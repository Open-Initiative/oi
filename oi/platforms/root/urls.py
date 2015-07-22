from django.conf.urls import *
from django.views.generic import TemplateView
# Activation de l'admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # contenu statique
    (r'^$', TemplateView.as_view(template_name="index-root.html")),
    (r'^cgu$', TemplateView.as_view(template_name="cgu.html")),
    (r'^contact$', TemplateView.as_view(template_name="contact.html")),
    (r'^presentation$', TemplateView.as_view(template_name="presentation.html")),
    # Pages des utilisateurs
    (r'^user/', include('oi.users.urls')),
    (r'^message/', include('oi.messages.urls')),
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
