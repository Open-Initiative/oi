#coding: utf-8
# Vues des messages
from django.http import HttpResponse
from oi.messages.models import Message, OI_SCORE_ADD, OI_SCORE_DEFAULT_RELEVANCE
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
    """Edit view of the message"""
    parents=""
    if request.GET.has_key("parents"):
        parents = request.GET["parents"]
    return render_to_response('messages/editmessage.html',{'id':0, 'divid':request.GET["divid"], 'parents':parents})

def savemessage(request, id=0):
    """Save the edited message and redirects to its view"""
    author = None
    if request.user.is_authenticated():
        author=request.user
    text = oiescape(request.POST["message"])
    message = Message(title = request.POST["title"], text = text, author=author, relevance=OI_SCORE_DEFAULT_RELEVANCE)
    message.save()
    if request.POST.has_key("parents") and request.POST["parents"]!='':
        map(message.parents.add, request.POST["parents"].split(","))
    message.add_expertise(request.user, OI_SCORE_ADD, True)
    message.current_user_has_voted = True
    return render_to_response('messages/message.html',{'message' : message})

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
