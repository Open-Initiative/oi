#coding: utf-8
# Vues des projets
from oi.settings import MEDIA_ROOT, TEMP_DIR
from oi.projects.models import Project, Spec, OINeedsPrjPerms
from oi.messages.models import Message, OI_READ, OI_ANSWER, OI_WRITE
from oi.messages.templatetags.oifilters import oiescape
from oi.users.models import User
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from datetime import timedelta
from django.views.generic.list_detail import object_detail
from django.core.files import File
from time import time
from urllib import quote
import os

def editproject(request, id):
    """Edit template of the project"""
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
        project = Project(title = request.POST["title"], author=author, parent=parent, message=message, public=True)
        
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
    return HttpResponseRedirect('/project/get/%s'%project.id)

@OINeedsPrjPerms(OI_WRITE)
def deleteproject(request, id):
    """Deletes the project given by id"""
    Project.objects.get(id=id).delete()
    return HttpResponseRedirect('/')

@OINeedsPrjPerms(OI_WRITE)
def finishproject(request, id):
    """Marks the project as finished"""
    project = Project.objects.get(id=id)
    project.progress = 1.
    project.save()
    return HttpResponse("Projet terminé")

@OINeedsPrjPerms(OI_READ)
def projectview(request, id):
    """Shows the project summary"""
    project = Project.objects.get(id=id)
    days = [project.start_date+timedelta(n) for n in range((project.due_date-project.start_date).days)]
    return render_to_response('projects/prjview.html',{'user':request.user, 'project':project, 'days':days})

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
