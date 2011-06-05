#coding: utf-8
# Vues des messages
import os
from time import time
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from oi.helpers import OI_PAGE_SIZE, OI_ALL_PERMS, OI_READ, OI_WRITE, OI_ANSWER, ajax_login_required
from oi.helpers import OI_SCORE_ADD, OI_SCORE_DEFAULT_RELEVANCE, OI_EXPERTISE_FROM_ANSWER, OI_EXPERTISE_TO_MESSAGE
from oi.settings import MEDIA_ROOT, MEDIA_URL
from oi.notification import models as notification
from oi.messages.models import Message, PromotedMessage, OINeedsMsgPerms
from oi.messages.templatetags.oifilters import oiescape, summarize

#OIMsgActions = [
#    OIAction(func="vote", icon="relevantmsg.png", show=lambda message,user: not message|ip_has_voted:request.META.REMOTE_ADDR and user.is_anonymous or not message|has_voted:user and user.is_authenticated,extra_param=1,  title=_("Message relevant")),
#    OIAction(func="vote", icon="irrelevantmsg.png", show=lambda message,user: not message|ip_has_voted:request.META.REMOTE_ADDR and user.is_anonymous or not message|has_voted:user and user.is_authenticated, extra_param=-1, title=_("Message irrelevant")),
#    OIAction(func="addMessage", icon="answermsg.png", show=lambda message,user: message|can_answer:user, title=_("Answer this message")),
#    OIAction(func="hideMessage", icon="privatemsg.png", show=lambda message,user: message|can_write:user and message.public, title=_("Make this message private")),
#    OIAction(func="shareMessage", icon="sharemsg.png",show=lambda message,user: message|can_write:user and not message.public,  title=_("Share this message")),
#    OIAction(func="deleteMessage", icon="delmsg.png", show=lambda message,user: message|can_write:user, title=_("Delete this message")),
#    OIAction(func="editMessage", icon="editmsg.png", show=lambda message,user: message|can_write:user, title=_("Correct this message")),
#    OIAction(func="observeMessage", icon="favmsg.png", title=_("Follow this message"))]

#def getmessages(request):
#    """Apply filter to message list"""
#    datemin = datetime.strptime(request.GET.get("datemin","2000,1,1"),"%Y,%m,%d")
#    datemax = datetime.strptime(request.GET.get("datemax","2100,1,1"),"%Y,%m,%d")
#    messages = Message.objects.filter(created__gte=datemin, created__lte=datemax, category=False, public=True)
#    promotedmsg = PromotedMessage.objects.filter(location="index")

#    ancestors = [id for id in request.GET.get("categs","").split(",") if id!=""] #ancestors separated by a comma in the parameters
#    if ancestors:
#        messages = messages.filter(ancestors__in=ancestors).distinct()
#        
#    return object_list(request, queryset=messages.order_by("-relevance")[:10], extra_context={'promotedmsg': promotedmsg})

@OINeedsMsgPerms(OI_READ)
def getmessage(request, id):
    """Message given by id"""
    message = Message.objects.get(id=id)
    depth = request.GET.get('depth',OI_PAGE_SIZE)
    mode = request.GET.get("mode","")
    
#    if message.category:
#        return HttpResponseRedirect("/index/%s"%id)
    if mode == "small":
        return render_to_response('messages/messagesmall.html',{'message':message, 'depth':depth})
    extra_context={'object':message, 'depth':depth, 'is_ajax':request.GET.get("mode")}
    return direct_to_template(request, template="messages/message_detail.html", extra_context=extra_context)

#def newmessage(request):
#    """Shows the new message form"""
#    return direct_to_template(request, template='messages/newmessage.html',extra_context={'categs':request.GET.get("categs","").split(",")})

def editmessage(request, id):
    """Edit form of the message"""
    message=None
    parentid = request.GET.get("parent","")
    if parentid:
        title = Message.objects.get(id=parentid).title
        while title[:4] == "Re: ":
            title = title[4:]
        message = Message(title = "Re: %s"%title)
    if id!='0':
        message = Message.objects.get(id=id)
        if not message.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden('Forbidden')
    return direct_to_template(request, template='messages/editmessage.html',extra_context={'message':message})

def savemessage(request, id):
    """Saves the edited message and redirects to its view"""
    author = None
    if request.user.is_authenticated():
        author=request.user
    text = oiescape(request.POST["message"])
    
    if id!='0': #existing message
        message = Message.objects.get(id=id)
        if not message.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden(_("Forbidden"))
        message.title = request.POST["title"]
        message.text = text
        if request.POST.get("rfp") == "True":
            message.rfp = True
        message.save()
    
    else: #new message
        parent = None
        if request.POST.get("parent"): #Checking parent rights
            parent = Message.objects.get(id=request.POST["parent"])
            if not parent.has_perm(request.user, OI_ANSWER):
                return HttpResponseForbidden(_("Forbidden"))

        #Creating the message
        if request.user.is_anonymous() or not parent:
            relevance = OI_SCORE_DEFAULT_RELEVANCE
        else:
            relevance = parent.get_expertise(request.user) * OI_EXPERTISE_TO_MESSAGE
        message = Message(title = request.POST["title"], text = text, author=author, public=True, parent=parent, relevance=relevance)
        if request.POST.get("rfp") == "True":
            message.rfp = True
        message.save()
        message.set_perm(author, OI_ALL_PERMS)
        
        #Adding expertise to user and parent's author
        if parent:
            parent.add_expertise(parent.author, message.get_expertise(request.user)*OI_EXPERTISE_FROM_ANSWER, False)
        message.add_expertise(request.user, OI_SCORE_ADD, True)

    if request.user.is_anonymous(): #notification from anonymous
        recipients = User.objects.filter(userprofile__observed_messages__descendants = message).distinct()
        notification.send(recipients, "answer", {'message':message, 'param':message.title}, True, None)
    else:
        #notify users about this message
        request.user.get_profile().msg_notify_all(message, "answer", message.title)
        #adds the message to user's observation
        request.user.get_profile().observed_messages.add(message)

    #affiche le nouveau message en retour
    return render_to_response('messages/message.html',{'message' : message}, context_instance=RequestContext(request))

@OINeedsMsgPerms(OI_WRITE)
def deletemessage(request, id):
    """Deletes the message and outputs a message"""
    Message.objects.get(id=id).delete()
    return HttpResponse(_(u"Message deleted"))

@OINeedsMsgPerms(OI_WRITE)
def hidemessage(request, id):
    """Makes the message private and outputs a message"""
    message = Message.objects.get(id=id)
    message.public = False
    message.save()
    return HttpResponse(_(u"Message is now private"))

@OINeedsMsgPerms(OI_WRITE)
def sharemessage(request, id):
    """Shares the message with a user and outputs a message"""
    message = Message.objects.get(id=id)
    user = User.objects.get(username=request.POST["username"])
    message.set_perm(user, OI_ALL_PERMS)
    return HttpResponse(_(u"Message shared"))

@ajax_login_required
@OINeedsMsgPerms(OI_READ)
def observemessage(request, id):
    """adds the message in the observe list of the user"""
    message = Message.objects.get(id=id)
    if request.POST.has_key("stop"):
        request.user.get_profile().observed_messages.remove(message)
        return HttpResponse(_("Stopped following"))
    else:
        request.user.get_profile().observed_messages.add(message)
        return HttpResponse(_("Following the message"))
    
@OINeedsMsgPerms(OI_WRITE)
def movemessage(request, id):
    """Adds a parent to the message"""
    message = Message.objects.get(id=id)
    parent = Message.objects.get(id=request.POST["parentid"])
    if not parent.has_perm(request.user, OI_ANSWER):
        return HttpResponseForbidden(_("Forbidden"))

    if message in parent.ancestors.all():
        return HttpResponse(_(u"Can not move a message to its answer"))
    message.parent = parent
    message.save() # to recompute ancestors

    #notify users about this message
    request.user.get_profile().msg_notify_all(parent, "answer", message.title)

    return HttpResponse(_(u"Message moved"))

#@OINeedsMsgPerms(OI_WRITE)
#def orphanmessage(request, id):
#    """Removes a parent of the message"""
#    message = Message.objects.get(id=id)
#    parent = Message.objects.get(id=request.POST["parentid"])
#    if parent not in message.parents.all():
#        return HttpResponse(u"Ce n'est pas une réponse du message")
#    if message.parents.count() < 2:
#        return HttpResponse(u"Ne peut pas laisser ce message orphelin")
#    message.parents.remove(parent)
#    message.save() # to recompute ancestors
#    return HttpResponse(u"Réponse retirée")

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
    image = open("%s%.0f_%s"%(MEDIA_ROOT,ts,uploadedfile.name), 'wb+')
    for chunk in uploadedfile.chunks():
        image.write(chunk)
    image.close()
    return render_to_response('messages/setFile.html', {'filename':"%.0f_%s"%(ts,uploadedfile.name)})

def getFile(request, filename):
    """gets a file in the FS for download"""
    response = HttpResponse(mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s'%filename
    response['X-Sendfile'] = "%s%s"%(MEDIA_ROOT,filename)
    response['Content-Length'] = os.path.getsize("%s%s"%(MEDIA_ROOT,filename))
    return response

def listcategories(request, id='0'):
    """List all the category messages"""
    if id=='0':
        categories = Message.objects.filter(category=True, parent=None)
    else:
        categories = Message.objects.filter(category=True, parent=id)
    return render_to_response('messages/arbo.html',{'categories': categories.order_by("-relevance"), 'dest': request.GET.get("dest")}, context_instance=RequestContext(request))
    
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
