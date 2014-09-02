# coding: utf-8
import cStringIO as StringIO
from functools import wraps
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.db.models import DateTimeField
from django.template.loader import render_to_string
from django.utils.decorators import available_attrs
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from ho import pisa
from django.conf import settings

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
OI_PRJ_STATES = ((OI_PROPOSED, _("Proposed")), (OI_ACCEPTED, _("Accepted")), (OI_STARTED, _("Started")), (OI_DELIVERED, _("Delivered")), (OI_VALIDATED, _("Done")), (OI_CANCELLED, _("Cancelled")), (OI_POSTPONED, _("Delayed")), (OI_CONTENTIOUS, _("Contentious")),)
OI_PRJ_PHASES = ((OI_ACCEPTED, _("Design")), (OI_STARTED, _("Execution")), (OI_DELIVERED, _("Validation")), (OI_VALIDATED, _("Task done")),)

# Available views
OI_PRJ_VIEWS = ['overview','description','planning','team','budget', 'github']

# Available table_overview
OI_TABLE_OVERVIEW = ['title','state','due_date','assignee','offer','target']

# Project constants
OI_PRJ_DONE = 100
OI_CANCELLED_BID = -1
OI_NO_EVAL = -2
OI_ACCEPT_DELAY = -3
OI_COMMISSION = Decimal(".05")
OI_COM_ON_BID = OI_COMMISSION/(OI_COMMISSION+1)
OI_VAT_RATE = Decimal("19.6")

# Maximum displayed depth of a discussion
OI_PAGE_SIZE = 10

# User name display styles
OI_DISPLAYNAME_TYPES = ["%(username)s", "%(first)s %(last)s", "%(first)s %(last).1s."]

# Generic permission constants
OI_ALL_PERMS = -1
OI_RIGHTS = [OI_READ, OI_WRITE, OI_ANSWER, OI_BID, OI_MANAGE] = [1,2,4,5,6]
OI_PERMS = ((OI_READ, _("Reading")), (OI_WRITE, _("Writing")), (OI_ANSWER, _("Answering")), (OI_BID, _("Bidding")), (OI_MANAGE, _("Managing")))

#Spec types
TEXT_TYPE = 1
IMAGE_TYPE = 2
URL_TYPE = 3
VIDEO_TYPE = 4
DOC_TYPE = 5
BUG_REPORT_TYPE = 6
SPEC_TYPES =  {TEXT_TYPE:_("Text"), IMAGE_TYPE:_("Image"), URL_TYPE:_("Url link"), VIDEO_TYPE:_("Video"), DOC_TYPE:_("Document"), BUG_REPORT_TYPE:_("Bug report")}

class OIAction:
    def show(self, project, user):
        return True
    extra_param = None
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def to_date(value):
    return DateTimeField.to_python(DateTimeField(), value)

def ajax_login_required(function=None, keep_fields=None):
    """Similar decorator as login_required, using 333 as redirect Http code to be captured by javascript"""
    def decorator(f):
        @wraps(f, assigned=available_attrs(f))
        def new_f(request, id, *args, **kwargs):
            if request.user.is_authenticated():
                return f(request, id, *args, **kwargs)
            # if keep_fields, the function will check every field and will keep it after login 
            # to no forget the args
            if keep_fields:
                for field in keep_fields:
                    if field and request.POST.has_key(field):
                        request.session[field] = request.POST[field]
                # we can have two situations for the login case 
                # using ajax use 333 status      
                if request.is_ajax():
                    return HttpResponse('%s?%s=%s'%(settings.LOGIN_URL, REDIRECT_FIELD_NAME, request.build_absolute_uri()),status=333)
                # don't using ajax no need 333 status
                else:
                    return HttpResponseRedirect('%s?%s=%s'%(settings.LOGIN_URL, REDIRECT_FIELD_NAME, request.build_absolute_uri()))
                    
            return HttpResponse('%s?%s=%s%s'%(settings.LOGIN_URL, REDIRECT_FIELD_NAME, settings.REDIRECT_URL, id),status=333)
        return new_f
    if function:
        return decorator(function)
    return decorator

def fetch_resources(uri, rel):
    """Url transformation for pdf generation"""
    if uri.startswith("/user/getpicture"):  #special case for user pictures
        return settings.MEDIA_ROOT + uri.replace("/getpicture", "") + "/profile.jpg"
    return settings.TEMPLATE_DIRS + "users/pdf/" + uri
    
def render_to_pdf(template, extra_context):
    """renders a template to a pdf"""
    resbuffer = StringIO.StringIO()
    css = open(settings.TEMPLATE_DIRS[0]+"users/pdf/resume.css").read()
    pdf = pisa.CreatePDF(render_to_string(template, extra_context), dest=resbuffer, link_callback=fetch_resources, default_css=css)
    if pdf.err:
        raise Exception(_("PDF Transformation Error"))
    return resbuffer.getvalue()

def computeSHA(params):
    """compute the SHA signature of the params to check for request integrity"""
    new_dict = {}
    for key in params.keys():
        if params[key]: #removes empty values
            new_dict[key.upper()] = params[key] #Turns keys uppercase
    keys = sorted(new_dict.keys()) #sort them alphabetically
    chain = settings.SHA_KEY.join(map(lambda key: "%s=%s"%(key, new_dict[key]), keys))+settings.SHA_KEY #generates chain to compute SHA signature from
    return sha256(chain.encode("utf-8")).hexdigest().upper() #computes and turns signature uppercase
    
#simply the bidProject function for the redirect url  
def oi_redirecturl(request, url, msg=None):
    """Redirect to url with ajax or not"""
    if msg:
        messages.info(request, msg)
    if request.is_ajax():
        return HttpResponse(url, status=333)
    else:
        return HttpResponseRedirect(url)
