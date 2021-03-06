import logging
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import NoArgsCommand
from django.template import Context
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _, get_language, activate
from oi.projects.context_processors import constants
from oi.projects.models import Project

class Command(NoArgsCommand):
    help = "Send a welcome message to new project owners"
    
    def handle_noargs(self, **options):
        # the language is to be temporarily switched to the recipient's language
        current_language = get_language()
        for project in Project.objects.filter(author__userprofile__contacted=False).filter(parent=None):
            if project.author.get_profile().contacted == False:
                activate(project.author.get_profile().language)
                
                # update context with site information
                current_site = "%s://%s"%(getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http"), Site.objects.get_current())
                context = Context(dict({"recipient": project.author, 'current_site': current_site, 'project': project}, **constants(None)))
                
                # e-mail data
                subject = _('New project on Open Funding')
                body = render_to_string('notification/email_new_project.txt', {'format': 'txt'}, context)
                body_html = render_to_string('notification/email_new_project.html', {'format': 'html'}, context)
                
                msg = EmailMultiAlternatives(subject, body, "contact@openinitiative.com", [project.author.email])
                msg.attach_alternative(body_html, "text/html")
                msg.send()
                
                # e-mail follow by admin
                msg_follow = EmailMultiAlternatives(subject, body, "contact@openinitiative.com", ["contact@openinitiative.com"])
                msg_follow.attach_alternative(body_html, "text/html")
                msg_follow.send()
                
                project.author.get_profile().contacted = True
                project.author.get_profile().save()
                
            # reset environment to original language
            activate(current_language)
