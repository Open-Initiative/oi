#coding: utf-8
# Vues des messages
from oi.messages.models import Message, PromotedMessage, OI_SCORE_ADD, OI_SCORE_DEFAULT_RELEVANCE, OI_EXPERTISE_FROM_ANSWER
from oi.messages.models import OI_ALL_PERMS, OI_READ, OI_WRITE, OI_ANSWER, OINeedsMsgPerms
from oi.messages.templatetags.oifilters import oiescape
from oi.users.models import User
from oi.settings import MEDIA_ROOT, MEDIA_URL
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.db.models import get_app
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_detail, object_list
from django.views.generic.simple import direct_to_template
from time import time
from datetime import datetime
import os

OI_PAGE_SIZE = 10
notification = get_app( 'notification' )

def getmessages(request):
    """Apply filter to message list"""
    datemin = datetime.strptime(request.GET.get("datemin","2000,1,1"),"%Y,%m,%d")
    datemax = datetime.strptime(request.GET.get("datemax","2100,1,1"),"%Y,%m,%d")
    messages = Message.objects.filter(created__gte=datemin, created__lte=datemax, category=False, public=True)
    promotedmsg = PromotedMessage.objects.filter(location="index")

    ancestors = [id for id in request.GET.get("categs","").split(",") if id!=""] #parents séparés par des virgules dans les paramètres
    if ancestors:
        messages = messages.filter(ancestors__in=ancestors)
        
    return object_list(request, queryset=messages.order_by("-relevance")[:10], extra_context={'promotedmsg': promotedmsg})

@OINeedsMsgPerms(OI_READ)
def getmessage(request, id):
    """Message given by id"""
    if Message.objects.get(id=id).category:
        return HttpResponseRedirect("/index/%s"%id)
    extra_context={'depth': request.GET.get('depth',OI_PAGE_SIZE), 'base':"%sbase.html"%request.GET.get("mode","")}
    return object_detail(request, queryset=Message.objects, object_id=id, extra_context=extra_context)

def newmessage(request):
    """Shows the new message form"""
    return direct_to_template(request, template='messages/newmessage.html',extra_context={'categs':request.GET.get("categs","").split(",")})

def editmessage(request, id):
    """Edit form of the message"""
    parents=""
    message=None
    parents = request.GET.get("parents","") #parents séparés par des virgules dans les paramètres
    if parents!="":
        title = Message.objects.get(id=parents.split(",")[0]).title
        while title[:4] == "Re: ":
            title = title[4:]
        message = Message(title = "Re: %s"%title)
    if id!='0':
        message = Message.objects.get(id=id)
        if not message.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden('Permissions insuffisantes')
    return render_to_response('messages/editmessage.html',{'divid':request.GET["divid"], 'parents':parents, 'message':message}, context_instance=RequestContext(request))

def savemessage(request, id):
    """Saves the edited message and redirects to its view"""
    author = None
    if request.user.is_authenticated():
        author=request.user
    text = oiescape(request.POST["message"])
    
    #Modification du message
    if id!='0':
        message = Message.objects.get(id=id)
        message.title = request.POST["title"]
        message.text = text
        message.save()
    
    else: #message existant
        #Vérification des parents
        parents=None
        if request.POST.has_key("parents") and request.POST["parents"]!='':
            parents = request.POST["parents"].split(",")
            for parent in parents:
                if not Message.objects.get(id=parent).has_perm(request.user, OI_ANSWER):
                    return HttpResponseForbidden("Permissions insuffisantes")
        if parents is None:
            return HttpResponseForbidden("Merci de choisir une catégorie")

        #Création du message
        message = Message(title = request.POST["title"], text = text, author=author, public=True, relevance=OI_SCORE_DEFAULT_RELEVANCE)
        message.save()
        message.set_perm(author, OI_ALL_PERMS)
        
        #ajout des parents et de l'expertise
        for parent in parents:
            message.parents.add(parent)
            Message.objects.get(id=parent).add_expertise(Message.objects.get(id=parent).author, message.get_expertise(request.user)*OI_EXPERTISE_FROM_ANSWER, False)
        message.add_expertise(request.user, OI_SCORE_ADD, True)
    
    #affiche le nouveau message en retour
    return render_to_response('messages/message.html',{'message' : message}, context_instance=RequestContext(request))

@OINeedsMsgPerms(OI_WRITE)
def deletemessage(request, id):
    """Deletes the message and outputs a message"""
    Message.objects.get(id=id).delete()
    return HttpResponse(u"Message supprimé")

@OINeedsMsgPerms(OI_WRITE)
def hidemessage(request, id):
    """Makes the message private and outputs a message"""
    message = Message.objects.get(id=id)
    message.public = False
    message.save()
    return HttpResponse(u"Message privé")

@OINeedsMsgPerms(OI_WRITE)
def sharemessage(request, id):
    """Shares the message with a user and outputs a message"""
    message = Message.objects.get(id=id)
    user = User.objects.get(username=request.POST["username"])
    message.set_perm(user, OI_ALL_PERMS)
    return HttpResponse(u"Message partagé")

@OINeedsMsgPerms(OI_WRITE)
def movemessage(request, id):
    """Adds a parent to the message"""
    message = Message.objects.get(id=id)
    parent = Message.objects.get(id=request.POST["parentid"])
    if message in parent.ancestors.all():
        return HttpResponse(u"Impossible de déplacer un message vers sa réponse")
    message.parents.add(parent)
    message.save() # to recompute ancestors
    return HttpResponse(u"Message déplacé")

@OINeedsMsgPerms(OI_WRITE)
def orphanmessage(request, id):
    """Removes a parent of the message"""
    message = Message.objects.get(id=id)
    parent = Message.objects.get(id=request.POST["parentid"])
    if parent not in message.parents.all():
        return HttpResponse(u"Ce n'est pas une réponse du message")
    if message.parents.count() < 2:
        return HttpResponse(u"Ne peut pas laisser ce message orphelin")
    message.parents.remove(parent)
    message.save() # to recompute ancestors
    return HttpResponse(u"Réponse retirée")

@OINeedsMsgPerms(OI_READ)
def vote(request, id):
    """Handles a user vote on a message"""
    message = Message.objects.get(id=id)
    if message.has_voted(request.user, request.META['REMOTE_ADDR']):
        return HttpResponse(u"déjà voté !")

    opinion = float(request.POST["opinion"])
    message.vote(request.user, opinion, request.META['REMOTE_ADDR'])
    message.save()
    return HttpResponse(u"A voté")

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
        categories = Message.objects.filter(category=True, parents=None)
    else:
        categories = Message.objects.filter(category=True, parents=id)
    return render_to_response('messages/arbo.html',{'categories': categories.order_by("-relevance"), 'dest': request.GET.get("dest")}, context_instance=RequestContext(request))
