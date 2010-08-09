#coding: utf-8
# Vues des messages
from django.http import HttpResponse, HttpResponseForbidden
from oi.messages.models import Message, OI_SCORE_ADD, OI_SCORE_DEFAULT_RELEVANCE, OI_MSG_READ, OI_MSG_WRITE, OI_MSG_ANSWER, OINeedsMsgPerms
from oi.messages.templatetags.oifilters import oiescape
from oi.projects.models import Project
from django.shortcuts import render_to_response

def getmessages(request):
    """All messages with no partents"""
    messages = Message.objects.filter(parents=None, category=False)
    projects = Project.objects.filter(parent=None)
    for message in messages:
        message.current_user_has_voted = message.has_voted(request.user, request.META['REMOTE_ADDR'])
        message.text = message.text
    return render_to_response('index.html',{'user': request.user, 'messages': messages, 'projects': projects})

@OINeedsMsgPerms(OI_MSG_READ)
def getmessage(request, id):
    """Message given by id"""
    message = Message.objects.get(id=id)
    message.current_user_has_voted = message.has_voted(request.user, request.META['REMOTE_ADDR'])
    if request.GET.get("inline"):
        template = 'messages/message.html'
    else:
        template = 'messages/getmessage.html'
    return render_to_response(template,{'user': request.user, 'message' : message})

def editmessage(request, id):
    """Edit form of the message"""
    parents=""
    message=None
    if request.GET.has_key("parents"):
        parents = request.GET["parents"]
    if id!='0':
        message = Message.objects.get(id=id)
        if not message.has_perm(request.user, OI_MSG_WRITE):
            return HttpResponseForbidden('Permissions insuffisantes')
    return render_to_response('messages/editmessage.html',{'divid':request.GET["divid"], 'parents':parents, 'message':message})

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
                if not Message.objects.get(id=parent).has_perm(request.user, OI_MSG_ANSWER):
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
    return render_to_response('messages/message.html',{'message' : message})

@OINeedsMsgPerms(OI_MSG_WRITE)
def deletemessage(request, id):
    """Deletes the message and output a message"""
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
    return render_to_response('messages/arbo.html',{'categories': categories})
