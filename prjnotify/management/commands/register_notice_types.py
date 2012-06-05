import logging
from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _
from oi.prjnotify.models import NoticeType

class Command(NoArgsCommand):
    help = "Create all notice types in database."
    
    def handle_noargs(self, **options):
        NoticeType.register("invitation", _(u"Invitation"), _(u"A user wishes to add you to his contacts"))
        NoticeType.register("invitation_accepted", _(u"Invitation accepted"), _(u"You have a new contact"))
        NoticeType.register("personal_message", _(u"Personal message"), _(u"You have received a personal message"))
        NoticeType.register("answer", _(u"Message posted"), _(u"A message has been posted in a subject you follow"))
        NoticeType.register("new_project", _(u"New project"), _(u"A new project has been proposed in a subject you follow"))
        NoticeType.register("delegate", _(u"Project delegated"), _(u"A project has been offered to be delegated to you"))
        NoticeType.register("answerdelegate", _(u"Answer to the delegation"), _(u"The user has answered your delegation offer"))
        NoticeType.register("answerdelay", _(u"Answer to your delay request"), _(u"Your delay request has been answered"))
        NoticeType.register("project_modified", _(u"Project changed"), _(u"A project you follow has been changed"))
        NoticeType.register("project_bid", _(u"Bid on the project"), _(u"A project you follow has been bid on"))
        NoticeType.register("project_state", _(u"Project progress"), _(u"A project you follow has changed state"))
        NoticeType.register("project_eval", _(u"Project evaluation"), _(u"A user has evaluated your project"))
        NoticeType.register("project_bid_cancel", _(u"Bid cancelled"), _(u"A user has cancelled his bis on a project"))
        NoticeType.register("project_cancel", _(u"Project cancelled"), _(u"A user has requested the project to be cancelled"))
        NoticeType.register("project_spec", _(u"Specification changed"), _(u"The specification of a project you follow has been changed"))
        NoticeType.register("share", _(u"Project shared"), _(u"The project has been shared with"))
