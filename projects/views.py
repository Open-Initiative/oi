#coding: utf-8
# Vues des projets
from oi.settings import MEDIA_ROOT
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden
from oi.projects.models import Project, Spec, OINeedsPrjPerms, OI_READ, OI_WRITE
from oi.messages.models import Message
from oi.users.models import User
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from datetime import time, timedelta
from os import rename
from urllib import quote

@OINeedsPrjPerms(OI_WRITE)
def editproject(request, id):
    """Edit template of the project"""
    project=None
    if id!='0':
        project = Project.objects.get(id=id)
    return render_to_response('projects/editproject.html',{'user': request.user, 'parent':request.GET.get("parent"), 'message':request.GET.get("message"), 'project':project})

@OINeedsPrjPerms(OI_WRITE)
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
        project = Project(title = request.POST["title"], author=author, parent=parent, message=message, public=True,
            start_date=request.POST.get("start_date"), due_date=request.POST.get("due_date"))
        
    else: #existing project
        project = Project.objects.get(id=id)
        project.title = request.POST["title"]
        project.start_date = request.POST.get("start_date")
        project.due_date = request.POST.get("due_date")

    if request.POST.has_key("assignee"):
        project.assignee = User.objects.get(username=request.POST["assignee"])

    project.save()
    return HttpResponseRedirect(reverse('oi.projects.views.getproject',args=(project.id,)))

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
def editspec(request, id, specid):
    """Edit template of a spec contains a spec details edit template"""
    divid = request.GET["divid"]
    project = Project.objects.get(id=id)
    return render_to_response('projects/editspec.html',{'user': request.user, 'divid': divid, 'specid':specid, 'project':project, 'types':Spec.TYPES, 'specorder':request.GET["specorder"]})

@OINeedsPrjPerms(OI_WRITE)
def editspecdetails(request, id, specid):
    """Edit template of a spec detail, ie: text, image, file..."""
    divid = request.GET["divid"]
    type = int(request.GET["type"])
    project = Project.objects.get(id=id)
    return render_to_response('projects/edit%s.html'%(Spec.TYPES[type].replace("é","e")),{'user': request.user, 'divid': divid, 'project':project})

@OINeedsPrjPerms(OI_WRITE)
def uploadfile(request, id, specid=0):
    """temporarily stores a file to be used in a spec"""
    uploadedfile = request.FILES['file']
    divid = request.POST['divid']
    filename = "%s_%s"%(time(),uploadedfile.name)
    tempfile = open('/home/lamp/tmp/%s'%filename, 'wb+')
    for chunk in uploadedfile.chunks():
        tempfile.write(chunk)
    tempfile.close()
    return HttpResponse('<script>window.parent.document.getElementById("filename_%s").value="%s"</script>'%(divid,filename))

@OINeedsPrjPerms(OI_WRITE)
def savespec(request, id, specid=0):
    """saves the spec"""
    author = None
    if request.user.is_authenticated():
        author=request.user
    project = Project.objects.get(id=id)
    filename = request.POST.get("filename")
    if filename:
        rename("/home/lamp/tmp/%s"%filename,MEDIA_ROOT+filename)
    
    order = int(request.POST["order"])
    if order==-1:
        order = project.get_max_order()+1
    else:
        order += 1
        project.insert_spec(order)
    
    spec = Spec(text = request.POST["text"], url = request.POST.get("url"), image = request.POST.get("image"), file = filename, author=author, project=project, order=order, type=request.POST["type"])
    spec.save()
    return render_to_response('projects/spec.html',{'user': request.user, 'project' : project, 'spec' : spec})

@OINeedsPrjPerms(OI_WRITE)
def deletespec(request, id, specid):
    """deletes the spec"""
    Spec.objects.get(id=specid).delete()
    return HttpResponse('Supprimé')
    
@OINeedsPrjPerms(OI_READ)
def getfile(request, filename):
    """gets a file in the FS for download"""
    response = HttpResponse(mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s'%quote(filename)
    response['X-Sendfile'] = quote(MEDIA_ROOT+filename)
    response['Content-Length'] = 0
    return response
