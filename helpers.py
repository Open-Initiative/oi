# coding: utf-8
import cStringIO as StringIO
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from notification import models as notification
from ho import pisa
from oi.settings import MEDIA_ROOT, TEMPLATE_DIRS

# Constantes de transmission de pertinence
OI_SCORE_ANONYMOUS = 1. #Score du vote anonyme
OI_SCORE_DEFAULT_RELEVANCE = 10. #Pertinence par défaut des messages
OI_SCORE_ADD = 3. #Score au contributeur
OI_SCORE_VOTE = 2. #Score au votant
OI_SCORE_FRACTION_TO_PARENT = .5 #Fraction montante
OI_SCORE_FRACTION_FROM_PARENT = .5 #Fraction descendante
OI_EXPERTISE_TO_MESSAGE = .02 #Transmission d'expertise au message
OI_EXPERTISE_TO_AUTHOR = .02 #Transmission d'expertise à l'auteur
OI_EXPERTISE_FROM_ANSWER = .002 #Fraction transmise par une réponse

# States of project workflow
[OI_PROPOSED, OI_ACCEPTED, OI_STARTED, OI_DELIVERED, OI_VALIDATED,  OI_CANCELLED, OI_POSTPONED, OI_CONTENTIOUS] = [0,1,2,3,4,11,12,99]
OI_PRJ_STATES = ((OI_PROPOSED, "Proposé"), (OI_ACCEPTED, "Accepté"), (OI_STARTED, "Démarré"), (OI_DELIVERED, "Livré"), (OI_VALIDATED, "Validé"), (OI_CANCELLED, "Annulé"), (OI_POSTPONED, "Retardé"), (OI_CONTENTIOUS, "Litigieux"),)

# Maximum displayed depth of a discussion
OI_PAGE_SIZE = 10

# Generic permission constants
OI_ALL_PERMS = -1
OI_RIGHTS = [OI_READ, OI_WRITE, OI_ANSWER] = [1,2,4]
OI_PERMS = ((OI_READ, "Lecture"), (OI_WRITE, "Ecriture"), (OI_ANSWER, "Réponse"),)

def fetch_resources(uri, rel):
    """Url transformation for pdf generation"""
    if uri.startswith("/user/getpicture"):  #special case for user pictures
        return MEDIA_ROOT + uri.replace("/getpicture", "") + "/profile.jpg"
    return TEMPLATE_DIRS + "users/pdf/" + uri
    
def render_to_pdf(template, extra_context):
    """renders a template to a pdf"""
    resbuffer = StringIO.StringIO()
    css = open(TEMPLATE_DIRS+"users/pdf/resume.css").read()
    pdf = pisa.CreatePDF(render_to_string(template, extra_context), dest=resbuffer, link_callback=fetch_resources, default_css=css)
    if pdf.err:
        raise Exception("PDF Transformation Error")
    return resbuffer.getvalue()
