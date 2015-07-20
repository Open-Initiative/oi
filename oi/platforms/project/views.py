#coding: utf-8
# Vues des projets
from random import random
import os
import logging
from time import time
from datetime import datetime,timedelta
from decimal import Decimal, InvalidOperation
from github import Github
from urllib import quote, urlencode
from urllib2 import Request, urlopen
from unicodedata import normalize
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.contrib.sites.models import get_current_site
from django.core import serializers
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404, QueryDict
from django.shortcuts import render_to_response, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.simplejson import JSONEncoder, JSONDecoder
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView
from django.template import RequestContext
from oi.helpers import OI_PRJ_STATES, OI_PROPOSED, OI_ACCEPTED, OI_STARTED, OI_DELIVERED, OI_VALIDATED, OI_CANCELLED, OI_POSTPONED, OI_CONTENTIOUS, OI_TABLE_OVERVIEW, OI_PRJDIALOGUES
from oi.helpers import OI_PRJ_DONE, OI_NO_EVAL, OI_ACCEPT_DELAY, OI_READ, OI_ANSWER, OI_BID, OI_MANAGE, OI_WRITE, OI_ALL_PERMS, OI_CANCELLED_BID, OI_COM_ON_BID, OI_COMMISSION
from oi.helpers import OI_PRJ_VIEWS, SPEC_TYPES, OIAction, ajax_login_required, oi_redirecturl
from oi.projects.models import Project, Spec, Spot, Bid, PromotedProject, OINeedsPrjPerms, Release, GitHubSync, Reward, RewardForm
from oi.messages.models import Message
from oi.messages.templatetags.oifilters import oiescape, summarize
from oi.prjnotify.models import Observer
from oi.settings_common import OI_GITHUB_ID, OI_GITHUB_SECRET, MEDIA_ROOT
import re

@OINeedsPrjPerms(OI_READ)
def getproject(request, id, view="overview"):
    if not view: view = "overview"
    project = Project.objects.get(id=id)
    extra_context = {'object': project, 'current_view':view, 'views':OI_PRJ_VIEWS, 'types':SPEC_TYPES, 'prjdialogues': OI_PRJDIALOGUES, 'table_overview': OI_TABLE_OVERVIEW, 'release': request.session.get("releases", {}).get(str(project.master.id), project.master.target.name if project.master.target else None)}
    return TemplateResponse(request, "projects/project_detail.html", extra_context)

@login_required
def editproject(request, id):
    """Shows the Edit template of the project"""
    project=None
    if id!='0':
        project = Project.objects.get(id=id)
        if not project.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden(_("Forbidden"))
            
    request_dict = QueryDict(request.body)
    if request.method == "GET":
        extra_context = {'user': request.user, 'parent':request_dict.get("parent"), 'project':project}
        return TemplateResponse(request, 'projects/editproject.html', extra_context)

@OINeedsPrjPerms(OI_WRITE)
def editspec(request, id, specid):
    """Edit template of a spec contains a spec details edit template"""
    spec=None
    order = request.GET.get("specorder")
    if specid!='0':
        spec = get_object_or_404(Spec, id=specid)
        if spec.project.id != int(id):
            return HttpResponse(_("Wrong arguments"), status=531)
        order = spec.order
    extra_context = {'divid': request.GET["divid"], 'spec':spec, 'specorder':order, 'project':Project.objects.get(id=id)}
    return TemplateResponse(request, 'projects/spec/editspec.html', extra_context)

@OINeedsPrjPerms(OI_WRITE)
def editspecdetails(request, id, specid):
    """Edit template of a spec detail, ie: text, image, file..."""
    type = int(request.GET["type"])
    project = Project.objects.get(id=id)
    spec=None
    if specid!='0':
        if project.state > OI_ACCEPTED:
            return HttpResponse(_("Can not change a task already started"), status=431)
        spec = Spec.objects.get(id=specid)
        if spec.project.id != int(id):
            return HttpResponse(_("Wrong arguments"), status=531)
    extra_context = {'user': request.user, 'divid': request.GET["divid"], 'project':project, 'spec':spec}
    return TemplateResponse(request, 'projects/spec/edit_type%s.html'%(type), extra_context)

class OIFeed(Feed):
    """generates RSS feed"""
    title = "Open Initiative"
    link = "http://openinitiative.com/"
    description = _(u"Latest updates of Open Initiative ")
    id = None
    
    def __new__(cls, request, id):
        obj = super(Feed, cls).__new__(cls)
        obj.id=id
        if id != '0':
            obj.description += " - " + Project.objects.get(id=id).title
        return obj(request)

    def get_object(self, request, *args, **kwargs):
        if self.id=='0':
            return None
        else:
            return Project.objects.get(id=self.id)

    def items(self, obj):
        if obj:
            return obj.descendants.order_by('-created')[:20]
        else:
            return Project.objects.order_by('-created')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        desc = _("Created by") + " " + item.author.get_profile().get_display_name()
        for spec in item.spec_set.all():
            desc += "\n- " + summarize(spec.text)
        return desc
        
    def item_link(self, item):
        return "/prjmgt/%s"%item.id   
