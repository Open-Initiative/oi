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


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("invitation", _(u"Invitation"), _(u"Un utilisateur souhaite entrer en contact avec vous"))
        notification.create_notice_type("invitation_accepted", _(u"Invitation acceptée"), _(u"Vous avez un nouveau contact"))
        notification.create_notice_type("personal_message", _(u"Message reçu"), _(u"Vous avez reçu un message"))
        notification.create_notice_type("answer", _(u"Message publié"), _(u"Un message a été publié sur un sujet que vous suivez."))
        notification.create_notice_type("new_project", _(u"Nouveau projet"), _(u"Un nouveau projet a été proposé dans un sujet que vous suivez."))
        notification.create_notice_type("project_modified", _(u"Projet modifié"), _(u"Un projet que vous suivez a été modifié."))
        notification.create_notice_type("project_bid", _(u"Mise sur le projet"), _(u"Un projet vous suivez a reçu une mise."))
        notification.create_notice_type("project_state", _(u"Avancement du projet"), _(u"Un projet que vous suivez a changé d'état."))
        notification.create_notice_type("project_eval", _(u"Projet évalué"), _(u"Un utilisateur a évalué votre projet."))
        notification.create_notice_type("project_cancel", _(u"Annulation du projet"), _(u"Un utilisateur a demandé l'annulation du projet."))
        notification.create_notice_type("project_spec", _(u"Spécification du projet modifiée"), _(u"La spécification d'un projet que vous suivez a été modifiée."))

    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
