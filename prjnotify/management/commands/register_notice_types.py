import logging
from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _
from oi.prjnotify.models import create_notice_type

class Command(NoArgsCommand):
    help = "Create all notice types in database."
    
    def handle_noargs(self, **options):
        create_notice_type("invitation", _(u"Invitation"), _(u"A user wishes to add you to his contacts"))
        create_notice_type("invitation_accepted", _(u"Invitation accepted"), _(u"You have a new contact"))
        create_notice_type("personal_message", _(u"Personal message"), _(u"You have received a personal message"))
        create_notice_type("answer", _(u"Message posted"), _(u"A message has been posted in a subject you follow"))
        create_notice_type("new_project", _(u"New project"), _(u"A new project has been proposed in a subject you follow"))
        create_notice_type("delegate", _(u"Project delegated"), _(u"A project has been offered to be delegated to you"))
        create_notice_type("answerdelegate", _(u"Answer to the delegation"), _(u"The user has answered your delegation offer"))
        create_notice_type("answerdelay", _(u"Answer to your delay request"), _(u"Your delay request has been answered"))
        create_notice_type("project_modified", _(u"Project changed"), _(u"A project you follow has been changed"))
        create_notice_type("project_bid", _(u"Bid on the project"), _(u"A project you follow has been bid on"))
        create_notice_type("project_state", _(u"Project progress"), _(u"A project you follow has changed state"))
        create_notice_type("project_eval", _(u"Project evaluation"), _(u"A user has evaluated your project"))
        create_notice_type("project_bid_cancel", _(u"Bid cancelled"), _(u"A user has cancelled his bis on a project"))
        create_notice_type("project_cancel", _(u"Project cancelled"), _(u"A user has requested the project to be cancelled"))
        create_notice_type("project_spec", _(u"Specification changed"), _(u"The specification of a project you follow has been changed"))
