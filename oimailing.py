#!/usr/bin/python
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = "oi.settings"
sys.path.append('/home/oi')

import csv
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from oi.settings import DEFAULT_FROM_EMAIL

for line in csv.DictReader(open("mailinglist.csv")):
    from_email = "Open Initiative <contact@openinitiative.com>"
    subject = render_to_string("emailing/subject.txt", line).strip()
    text_content = render_to_string("emailing/emailing.txt", line)
    html_content = render_to_string("emailing/emailing.html", line)
    to_email = line['email']

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    if not msg.send():    
        print "error on %s"%to_email
