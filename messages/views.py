#coding: utf-8
# Vues des messages
from oi.messages.models import Message, OI_SCORE_ADD, OI_SCORE_DEFAULT_RELEVANCE, OI_READ, OI_WRITE, OI_ANSWER, OI_EXPERTISE_FROM_ANSWER, OINeedsMsgPerms
from oi.messages.templatetags.oifilters import oiescape
from oi.projects.models import Project
from oi.users.models import User
from oi.settings import MEDIA_ROOT, MEDIA_URL
from django.http import HttpResponse, HttpResponseForbidden
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

def index(request):
    """All messages with no partents"""
    messages = Message.objects.filter(category=False)[:10]
    projects = Project.objects.filter(parent=None)
    return render_to_response('index.html',{'messages': messages, 'projects': projects}, context_instance=RequestContext(request))

def getmessages(request):
    """Apply filter to message list"""
    datemin = datetime.strptime(request.GET.get("datemin","2000,1,1"),"%Y,%m,%d")
    datemax = datetime.strptime(request.GET.get("datemax","2100,1,1"),"%Y,%m,%d")
    messages = Message.objects.filter(created__gte=datemin, created__lte=datemax, category=False)

    parents = [id for id in request.GET.get("categs","").split(",") if id!=""] #parents séparés par des virgules dans les paramètres
    if parents:
        messages = messages.filter(parents__in=parents)
        
    return object_list(request, queryset=messages.order_by("-relevance")[:10]
)

@OINeedsMsgPerms(OI_READ)
def getmessage(request, id):
    """Message given by id"""
    extra_context={'depth': request.GET.get('depth',OI_PAGE_SIZE), 'base':"%sbase.html"%request.GET.get("mode","")}
    return object_detail(request, queryset=Message.objects, object_id=id, extra_context=extra_context)

def newmessage(request):
    """Shows the new message form"""
    return direct_to_template(request, template='messages/newmessage.html',extra_context={'parents':request.GET.get("parents","")})

def editmessage(request, id):
    """Edit form of the message"""
    parents=""
    message=None
    if request.GET.has_key("parents"):
        parents = request.GET["parents"]
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
    return render_to_response('messages/arbo.html',{'categories': categories}, context_instance=RequestContext(request))
