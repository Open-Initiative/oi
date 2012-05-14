# coding: utf-8
from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from django.contrib.sites.models import Site

def register_site(app, created_models, verbosity, **kwargs):
    if Site.objects.count() > 0:
        site = Site.objects.get_current()
    else:
        site = Site()
    site.domain = u"www.open-initiative.com"
    site.name = u"Open Initiative"
    site.save()
    
signals.post_syncdb.connect(register_site)

