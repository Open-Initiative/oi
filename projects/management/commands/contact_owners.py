import logging
from django.core.management.base import NoArgsCommand
from oi.projects.models import Project

class Command(NoArgsCommand):
    help = "Send message to new project owners"
    
    def handle_noargs(self, **options):
        for project in Project.objects.filter(author__userprofile__contacted=False):
            if not project.parent: # Email
                project.contact_new_owners()
