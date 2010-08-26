#coding: utf-8
# Vues des messages
from django.http import HttpResponse, HttpResponseForbidden
from oi.messages.models import Message, OI_SCORE_ADD, OI_SCORE_DEFAULT_RELEVANCE, OI_READ, OI_WRITE, OI_ANSWER, OINeedsMsgPerms
from oi.messages.templatetags.oifilters import oiescape
from oi.projects.models import Project
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_detail, object_list
from django.views.generic.simple import direct_to_template

OI_PAGE_SIZE = 10

def index(request):
    """All messages with no partents"""
    messages = Message.objects.filter(category=False)
    projects = Project.objects.filter(parent=None)
    return render_to_response('index.html',{'messages': messages, 'projects': projects}, context_instance=RequestContext(request))

def getmessages(request):
    """All messages with no partents"""
    messages = Message.objects.filter(parents__in=[id for id in request.GET.get("categs","").split(",") if id!=""], category=False)
    return object_list(request, queryset=messages)

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
        message.add_expertise(request.user, OI_SCORE_ADD, True)
        message.current_user_has_voted = True
    
    #affiche le nouveau message en retour
    return render_to_response('messages/message.html',{'message' : message}, context_instance=RequestContext(request))

@OINeedsMsgPerms(OI_WRITE)
def deletemessage(request, id):
    """Deletes the message and outputs a message"""
    Message.objects.get(id=id).delete()
    return HttpResponse(u"Message supprimé")

def vote(request, id):
    """Handles a user vote on a message"""
    message = Message.objects.get(id=id)
    if message.has_voted(request.user, request.META['REMOTE_ADDR']):
        return HttpResponse(u"déjà voté !")

    opinion = float(request.POST["opinion"])
    message.vote(request.user, opinion, request.META['REMOTE_ADDR'])
    message.save()
    return HttpResponse(u"A voté")

def listcategories(request, id='0'):
    """List all the category messages"""
    if id=='0':
        categories = Message.objects.filter(category=True, parents=None)
    else:
        categories = Message.objects.filter(category=True, parents=id)
    return render_to_response('messages/arbo.html',{'categories': categories}, context_instance=RequestContext(request))
