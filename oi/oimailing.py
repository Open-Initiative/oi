#!/usr/bin/python
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = "oi.settings"
sys.path.append('/home/oi')

from csv import DictReader
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.template.loader import render_to_string
from oi.settings import DEFAULT_FROM_EMAIL
from oi.users.models import Prospect

for line in DictReader(open("mailinglist.csv"), delimiter=';'):
    from_email = "Open Initiative <contact@openinitiative.com>"
    prospect, created = Prospect.objects.get_or_create(email = line['Adresse email'], defaults = {'kompassId':line['ID Kompass'], 'name':line['Contact']})
    if not created:
        print "%s already in database"%prospect.email
    
    else:
        subject = render_to_string("emailing/subject.txt", prospect.__dict__).strip()
        text_content = render_to_string("emailing/emailing.txt", prospect.__dict__)
        html_content = render_to_string("emailing/emailing.html", prospect.__dict__)
        to_email = prospect.email

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        if not msg.send():    
            print "error sending to %s"%to_email
