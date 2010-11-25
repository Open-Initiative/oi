# coding: utf-8
from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from django.contrib.sites.models import Site

def register_site(app, created_models, verbosity, **kwargs):
    site = Site.objects.get_current()
    site.domain = u"www.open-initiative.com"
    site.name = u"Open Initiative"
    site.save()
    
signals.post_syncdb.connect(register_site)


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("invitation", _("Nouveau contact"), _("Vous avez un nouveau contact"))
        notification.create_notice_type("message", _("Nouveau message"), _(u"Vous avez reçu un message"))
        notification.create_notice_type("answer", _(u"Réponse à votre message"), _(u"Une réponse a été apportée à un message que vous suivez"))
        notification.create_notice_type("prjdone", _(u"Projet terminé"), _(u"Le projet que vous suivez est terminé"))

    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
