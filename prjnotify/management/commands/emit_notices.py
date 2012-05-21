import logging
from django.core.management.base import NoArgsCommand
from oi.prjnotify.models import Observer

class Command(NoArgsCommand):
    help = "Emit queued notices."
    
    def handle_noargs(self, **options):
        for observer in Observer.objects.filter(notice__sent=None):
            if observer.should_send() and observer.user.email and observer.user.is_active: # Email
                observer.send()
