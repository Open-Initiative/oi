# coding: utf-8
from django.conf import settings
from django.db.models.signals import post_syncdb
from south.signals import post_migrate
from django.utils.translation import ugettext_noop as _
from django.contrib.sites.models import Site

def register_site(app, created_models=None, verbosity=None, **kwargs):
    for (name, domain) in settings.OI_DOMAINS:
        site, created = Site.objects.get_or_create(name = name)
        site.domain = domain
        site.save()
        if created:
            print "%s registered"%name
    
post_syncdb.connect(register_site)
post_migrate.connect(register_site)

