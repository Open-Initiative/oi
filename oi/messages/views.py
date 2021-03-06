#coding: utf-8
# Vues des messages
import os
from time import time
from datetime import datetime
from unicodedata import normalize
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.contrib.sites.models import get_current_site
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404, QueryDict
from django.template.response import TemplateResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, ListView
from oi.helpers import OI_PAGE_SIZE, OI_ALL_PERMS, OI_READ, OI_ANSWER, OI_WRITE, ajax_login_required, jsonld_array
from oi.helpers import OI_SCORE_ADD, OI_SCORE_DEFAULT_RELEVANCE, OI_EXPERTISE_FROM_ANSWER, OI_EXPERTISE_TO_MESSAGE
from oi.projects.models import Project
from oi.messages.models import Message, PromotedMessage, OINeedsMsgPerms
from oi.messages.templatetags.oifilters import oiescape, summarize

@OINeedsMsgPerms(OI_READ)
def getmessage(request, id):
    """Message given by id"""
    message = Message.objects.get(id=id)
    depth = request.GET.get('depth',OI_PAGE_SIZE)
    mode = request.GET.get("mode","")
    
    if mode == "small":
        return render_to_response('messages/messagesmall.html',{'message':message, 'depth':depth})
    extra_context={'object':message, 'depth':depth, 'is_ajax':request.GET.get("mode")}
    return TemplateResponse(request, "messages/message_detail.html", extra_context)
    
def ldpmessage(request, id):
    """Return jsonLd object"""
    message = get_object_or_404(Message, id=id)
    response = render_to_response("ldp/message.json", {
        "message": message,
        "current_site": get_current_site(request),
        "descendants": jsonld_array(request, message.descendants, "/message/ldpcontainer/"),
        "ancestors": jsonld_array(request, message.ancestors, "/message/ldpcontainer/"),
    })
    response["Content-Type"] = "application/ld+json"
    response["Access-Control-Allow-Origin"] = "*"
    return response

def editmessage(request, id):
    """Edit form of the message"""
    title=""
    message=None
    parentid = request.GET.get("parent","")
    if request.GET.get("project"):
        title = "Re: %s"%Project.objects.get(id=request.GET["project"]).title
    if parentid:
        title = Message.objects.get(id=parentid).title
        while title[:4] == "Re: ":
            title = title[4:]
        title = "Re: %s"%title
        message = Message(title=title)
    if id!='0':
        message = Message.objects.get(id=id)
        if not message.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden('Forbidden')
        title = message.title
    extra_context={'message':message, 'title':title}
    return TemplateResponse(request, 'messages/editmessage.html', extra_context)

def savemessage(request, id):
    """Saves the edited message and redirects to its view"""
    author = None
    project = None
    if request.user.is_authenticated():
        author=request.user
        
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        text = oiescape(request_dict["message"])
        
        if id!='0': #existing message
            message = Message.objects.get(id=id)
            if message.project and not message.project.has_perm(request.user, OI_ANSWER):
                return HttpResponseForbidden(_("Forbidden"))
            message.title = request_dict["title"]
            message.text = text
            message.save()
        
        else: #new message
            parent = None
            if request_dict.get("parent"): #Checking parent rights
                parent = Message.objects.get(id=request_dict["parent"])
                if parent.project and not parent.project.has_perm(request.user, OI_ANSWER):
                    return HttpResponseForbidden(_("Forbidden"))
            if request_dict.get("project"):
                project = Project.objects.get(id=request_dict["project"])
                if not project.has_perm(request.user, OI_ANSWER):
                    return HttpResponseForbidden(_("Forbidden"))

            #Creating the message
            if request.user.is_anonymous() or not parent:
                relevance = OI_SCORE_DEFAULT_RELEVANCE
            else:
                relevance = parent.get_expertise(request.user) * OI_EXPERTISE_TO_MESSAGE
            message = Message(title = request_dict["title"], text = text, author=author, parent=parent, project=project, relevance=relevance)
            message.save()
            
            #Adding expertise to user and parent's author
            if parent:
                parent.add_expertise(parent.author, message.get_expertise(request.user)*OI_EXPERTISE_FROM_ANSWER, False)
            message.add_expertise(request.user, OI_SCORE_ADD, True)
        
        #notify users about this message
        if project:
            project.notify_all(request.user, "answer", message.text)
            #adds the message to user's observation
            if author:
                author.get_profile().follow_project(project)
        for ancestor in message.ancestors.exclude(project=None):
            ancestor.project.notify_all(request.user, "answer", message.text)
            #adds the message to user's observation
            if author:
                author.get_profile().follow_project(ancestor.project)

        #affiche le nouveau message en retour
        return render_to_response('messages/message.html',{'message' : message}, context_instance=RequestContext(request))

@OINeedsMsgPerms(OI_WRITE)
def deletemessage(request, id):
    """Deletes the message and outputs a message"""
    Message.objects.get(id=id).delete()
    return HttpResponse(_(u"Message deleted"))

@OINeedsMsgPerms(OI_WRITE)
def movemessage(request, id):
    """Adds a parent to the message"""
    message = Message.objects.get(id=id)
    parent = Message.objects.get(id=request.POST["parentid"])

    if message in parent.ancestors.all():
        return HttpResponse(_(u"Can not move a message to its answer"))
    message.parent = parent
    message.save() # to recompute ancestors
    return HttpResponse(_(u"Message moved"))

@OINeedsMsgPerms(OI_READ)
def vote(request, id):
    """Handles a user vote on a message"""
    message = Message.objects.get(id=id)
    if message.has_voted(request.user, request.META['REMOTE_ADDR']):
        return HttpResponse(_(u"already voted!"))

    opinion = float(request.POST["opinion"])
    message.vote(request.user, opinion, request.META['REMOTE_ADDR'])
    message.save()
    return HttpResponse(_(u"voted"))

def uploadFile(request):
    """uploads an image on the server"""
    uploadedfile = request.FILES['image']
    ts = time()
    filename = normalize("NFKD", uploadedfile.name).encode('ascii', 'ignore').replace('"', '')
    image = open("%s%.0f_%s"%(settings.MEDIA_ROOT,ts,filename), 'wb+')
    for chunk in uploadedfile.chunks():
        image.write(chunk)
    image.close()
    return render_to_response('messages/setFile.html', {'filename':"%.0f_%s"%(ts,filename), 'fieldname': request.POST.get('fieldname')})

def getFile(request, filename):
    """gets a file in the FS for download"""
    response = HttpResponse(mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s'%filename
    response['X-Sendfile'] = "%s%s"%(settings.MEDIA_ROOT,filename)
    try:
        response['Content-Length'] = os.path.getsize("%s%s"%(settings.MEDIA_ROOT,filename))
    except OSError:
        raise Http404
    return response

def listancestors(request, id):
    """lists ancestors of the message in a string"""
    message = Message.objects.get(id=id)
    anclist = map(lambda x:x.id.__str__(),message.get_ancestors())
    return HttpResponse(",".join(anclist))

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
            obj.description += " - " + Message.objects.get(id=id).title
        return obj(request)

    def get_object(self, request, *args, **kwargs):
        if self.id=='0':
            return None
        else:
            return Message.objects.get(id=self.id)

    def items(self, obj):
        if obj:
            return obj.descendants.order_by('-created')[:10]
        else:
            return Message.objects.order_by('-created')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return summarize(item.text)
        
    def item_link(self, item):
        return "/message/get/%s"%item.id
