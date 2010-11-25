#coding: utf-8
# Vues des projets
from oi.settings import MEDIA_ROOT, TEMP_DIR
from oi.projects.models import Project, Spec, Bid, PromotedProject, OINeedsPrjPerms, OI_PROPOSED, OI_ACCEPTED, OI_STARTED, OI_DELIVERED, OI_VALIDATED
from oi.messages.models import Message, OI_READ, OI_ANSWER, OI_WRITE, OI_ALL_PERMS
from oi.messages.templatetags.oifilters import oiescape
from oi.users.models import User
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.db.models import Sum
from datetime import timedelta
from django.views.generic.list_detail import object_detail, object_list
from django.core.files import File
from time import time
from datetime import datetime
from decimal import Decimal
from urllib import quote
import os
    
def getprojects(request):
    """Apply filter to project list"""
    datemin = datetime.strptime(request.GET.get("datemin","2000,1,1"),"%Y,%m,%d")
    datemax = datetime.strptime(request.GET.get("datemax","2100,1,1"),"%Y,%m,%d")
    projects = Project.objects.filter(created__gte=datemin, created__lte=datemax, parent=None, public=True)
    if request.GET.has_key("state"):
        projects = projects.filter(state=request.GET["state"])

    ancestors = [id for id in request.GET.get("categs","").split(",") if id!=""] #parents séparés par des virgules dans les paramètres
    if ancestors:
        projects = projects.filter(message__ancestors__in=ancestors)

    promotedprj = PromotedProject.objects.filter(location="index")

    return object_list(request, queryset=projects[:10], extra_context={'promotedprj': promotedprj})

def editproject(request, id):
    """Shows the Edit template of the project"""
    project=None
    if id!='0':
        project = Project.objects.get(id=id)
        if not project.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden("Permissions insuffisantes")
    return render_to_response('projects/editproject.html',{'user': request.user, 'parent':request.GET.get("parent"), 'message':request.GET.get("message"), 'project':project})

def saveproject(request, id='0'):
    """Saves the edited project and redirects to it"""
    author = None
    parent = None
    if request.user.is_authenticated():
        author=request.user
    
    if id=='0': #new project
        #gets message from parent
        if request.POST.has_key("parent"):
            parent = Project.objects.get(id=request.POST["parent"])
            message = parent.message
        #or from query
        else:
            message = Message.objects.get(id=request.POST["message"])
        if not message.has_perm(request.user, OI_ANSWER):
            return HttpResponseForbidden("Permissions insuffisantes")
        project = Project(title = request.POST["title"], author=author, parent=parent, message=message, public=True, state=OI_PROPOSED)
        
    else: #existing project
        project = Project.objects.get(id=id)
        if not project.has_perm(request.user, OI_ANSWER):
            return HttpResponseForbidden("Permissions insuffisantes")
        project.title = request.POST["title"]

    if request.POST["assignee"] and len(request.POST["assignee"])>0:
        project.assignee = User.objects.get(username=request.POST["assignee"])
    if request.POST.has_key("start_date") and len(request.POST["start_date"])>0:
        project.start_date = request.POST["start_date"]
    if request.POST.has_key("due_date") and len(request.POST["due_date"])>0:
        project.due_date = request.POST["due_date"]
    if request.POST.has_key("progress") and len(request.POST["progress"])>0:
        project.progress = request.POST["progress"]

    project.save()
    project.set_perm(author, OI_ALL_PERMS)
    if request.POST.get("inline","0") == "1":
        return HttpResponseRedirect('/project/gettask/%s'%project.id)
    else:
        return HttpResponseRedirect('/project/get/%s'%project.id)

@OINeedsPrjPerms(OI_READ)
def bidproject(request, id):
    """Bids on the project"""
    project = Project.objects.get(id=id)
    bid = Bid(project=project, user=request.user, amount=0)
    bid.save()
    if project.state == OI_PROPOSED:
        # if the sum of bids is not less than the offer
        if not project.bid_set.aggregate(Sum("amount"))["amount__sum"].compare(project.offer).is_signed():
            project.state = OI_ACCEPTED
            project.save()
    return HttpResponse("Souscription enregistrée")

@OINeedsPrjPerms(OI_READ)
def startproject(request, id):
    """Starts the project"""
    project = Project.objects.get(id=id)
    if project.state == OI_ACCEPTED:
        # only the assignee can start the project
        if project.assignee == request.user:
            project.state = OI_STARTED
            project.save()
    return HttpResponse("Projet démarré")

@OINeedsPrjPerms(OI_WRITE)
def deliverproject(request, id):
    """Marks the project as delivered"""
    project = Project.objects.get(id=id)
    if project.state == OI_STARTED:
        # only the assignee can deliver the project
        if project.assignee == request.user:
            project.progress = 1.
            project.state = OI_DELIVERED
            project.save()
    return HttpResponse("Projet terminé")

@OINeedsPrjPerms(OI_READ)
def validateproject(request, id):
    """Validates the project by the user"""
    project = Project.objects.get(id=id)
    if project.state == OI_DELIVERED:
        for bid in Bid.objects.filter(user=request.user):
            bid.validated = True
            bid.save()
        # If there are no more users waiting for validation
        if project.bid_set.filter(validated=False).count()==0:
            project.state = OI_VALIDATED
            project.save()
    return HttpResponse("Validation enregistrée")

@OINeedsPrjPerms(OI_READ)
def evaluateproject(request, id):
    """Gives user's evaluation on the project"""
    project = Project.objects.get(id=id)
    if project.state == OI_VALIDATED:
        for bid in Bid.objects.filter(user=request.user):
            bid.rating = Decimal(request.POST["rating"])
            bid.save()
    return HttpResponse("Evaluation enregistrée")

@OINeedsPrjPerms(OI_WRITE)
def deleteproject(request, id):
    """Deletes the project given by id"""
    Project.objects.get(id=id).delete()
    return HttpResponseRedirect('/')

@OINeedsPrjPerms(OI_READ)
def projectview(request, id):
    """Shows the project summary"""
    project = Project.objects.get(id=id)
    days = [project.start_date+timedelta(n) for n in range((project.due_date-project.start_date).days)]
    return render_to_response('projects/prjview.html',{'user':request.user, 'project':project, 'days':days})

@OINeedsPrjPerms(OI_WRITE)
def hideproject(request, id):
    """Makes the project private and outputs a message"""
    project = Project.objects.get(id=id)
    project.public = False
    project.save()
    return HttpResponse(u"Project privé")

@OINeedsPrjPerms(OI_WRITE)
def shareproject(request, id):
    """Shares the project with a user and outputs a message"""
    project = Project.objects.get(id=id)
    user = User.objects.get(username=request.POST["username"])
    project.set_perm(user, OI_ALL_PERMS)
    return HttpResponse(u"Project partagé")

@OINeedsPrjPerms(OI_WRITE)
def editspec(request, id, specid):
    """Edit template of a spec contains a spec details edit template"""
    spec=None
    if specid!='0':
        spec = Spec.objects.get(id=specid)
    extra_context = {'divid': request.GET["divid"], 'spec':spec, 'types':Spec.TYPES, 'specorder':request.GET.get("specorder")}
    return object_detail(request, queryset=Project.objects, object_id=id, template_object_name='project', template_name='projects/editspec.html', extra_context=extra_context)

@OINeedsPrjPerms(OI_WRITE)
def editspecdetails(request, id, specid):
    """Edit template of a spec detail, ie: text, image, file..."""
    divid = request.GET["divid"]
    type = int(request.GET["type"])
    project = Project.objects.get(id=id)
    spec=None
    if specid!='0':
        spec = Spec.objects.get(id=specid)
    return render_to_response('projects/edit%s.html'%(Spec.TYPES[type].replace("é","e")),{'user': request.user, 'divid': divid, 'project':project, 'spec':spec})

@OINeedsPrjPerms(OI_WRITE)
def savespec(request, id, specid='0'):
    """saves the spec"""
    author = None
    if request.user.is_authenticated():
        author=request.user
    project = Project.objects.get(id=id)
    
    order = int(request.POST["order"])
    if order==-1:
        order = project.get_max_order()+1
    else:
        order += 1
        project.insert_spec(order)
    
    if specid=='0': #new spec
        spec = Spec(text = oiescape(request.POST["text"]), author=author, project=project, order=order, type=int(request.POST["type"]))
    else: #edit existing spec
        spec = Spec.objects.get(id=specid)
        spec.text = oiescape(request.POST["text"])
        
    if request.POST.has_key("url"):
        spec.url = request.POST["url"]
        
    filename = request.POST.get("filename")
    if filename:
        spec.file.delete()
        path = "%s%s_%s_%s"%(TEMP_DIR,request.user.id,request.POST["ts"],filename)
        spec.file.save(filename, File(open(path)), False)
        os.remove(path)
    spec.save()

    return render_to_response('projects/spec.html',{'user': request.user, 'project' : project, 'spec' : spec})

@OINeedsPrjPerms(OI_WRITE)
def deletespec(request, id, specid):
    """deletes the spec"""
    Spec.objects.get(id=specid).delete()
    return HttpResponse('Supprimé')
    
@OINeedsPrjPerms(OI_WRITE)
def uploadfile(request, id, specid='0'):
    """temporarily stores a file to be used in a spec"""
    uploadedfile = request.FILES['file']
    divid = request.POST['divid']
    ts = time()
    tempfile = open("%s%s_%s_%s"%(TEMP_DIR,request.user.id,ts,uploadedfile.name), 'wb+')
    for chunk in uploadedfile.chunks():
        tempfile.write(chunk)
    tempfile.close()
    return render_to_response('projects/fileframe.html',{'divid':divid,'filename':uploadedfile.name,'ts':ts,'projectid':id})

@OINeedsPrjPerms(OI_WRITE)
def deltmpfile(request, id):
    """deletes a temporary file"""
    path = "%s%s_%s_%s"%(TEMP_DIR,request.user.id,request.POST["ts"],request.POST["filename"])
    os.remove(path)
    return HttpResponse('Supprimé')

@OINeedsPrjPerms(OI_READ)
def getfile(request, id, filename):
    """gets a file in the FS for download"""
    response = HttpResponse(mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s'%filename
    response['X-Sendfile'] = "%sproject/%s/%s"%(MEDIA_ROOT,id,filename)
    response['Content-Length'] = os.path.getsize("%sproject/%s/%s"%(MEDIA_ROOT,id,filename))
    return response
