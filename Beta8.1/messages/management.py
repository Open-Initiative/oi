# coding: utf-8
from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from django.contrib.sites.models import Site
from oi.notification import models as notification

def register_site(app, created_models, verbosity, **kwargs):
    if Site.objects.count() > 0:
        site = Site.objects.get_current()
    else:
        site = Site()
    site.domain = u"www.open-initiative.com"
    site.name = u"Open Initiative"
    site.save()
    
signals.post_syncdb.connect(register_site)

def create_notice_types(app, created_models, verbosity, **kwargs):
    notification.create_notice_type("invitation", _(u"Invitation"), _(u"A user wishes to add you to his contacts"))
    notification.create_notice_type("invitation_accepted", _(u"Invitation accepted"), _(u"You have a new contact"))
    notification.create_notice_type("personal_message", _(u"Personal message"), _(u"You have received a personal message"))
    notification.create_notice_type("answer", _(u"Message posted"), _(u"A message has been posted in a subject you follow"))
    notification.create_notice_type("new_project", _(u"New project"), _(u"A new project has been proposed in a subject you follow"))
    notification.create_notice_type("delegate", _(u"Project delegated"), _(u"A project has been offered to be delegated to you"))
    notification.create_notice_type("answerdelegate", _(u"Answer to the delegation"), _(u"The user has answered your delegation offer"))
    notification.create_notice_type("answerdelay", _(u"Answer to your delay request"), _(u"Your delay request has been answered"))
    notification.create_notice_type("project_modified", _(u"Project changed"), _(u"A project you follow has been changed"))
    notification.create_notice_type("project_bid", _(u"Bid on the project"), _(u"A project you follow has been bid on"))
    notification.create_notice_type("project_state", _(u"Project progress"), _(u"A project you follow has changed state"))
    notification.create_notice_type("project_eval", _(u"Project evaluation"), _(u"A user has evaluated your project"))
    notification.create_notice_type("project__bid_cancel", _(u"Bid cancelled"), _(u"A user has cancelled his bis on a project"))
    notification.create_notice_type("project_cancel", _(u"Project cancelled"), _(u"A user has requested the project to be cancelled"))
    notification.create_notice_type("project_spec", _(u"Specification changed"), _(u"The specification of a project you follow has been changed"))

signals.post_syncdb.connect(create_notice_types, sender=notification)
