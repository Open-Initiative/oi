#coding: utf-8
# Vues des projets
import os
import logging
from time import time
from datetime import datetime,timedelta
from decimal import Decimal, InvalidOperation
from urllib import quote
from unicodedata import normalize
from django.core import serializers
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_detail, object_list
from django.views.generic.simple import direct_to_template
from oi.notification import models as notification
from oi.settings import MEDIA_ROOT, TEMP_DIR
from oi.helpers import OI_PRJ_STATES, OI_PROPOSED, OI_ACCEPTED, OI_STARTED, OI_DELIVERED, OI_VALIDATED, OI_CANCELLED, OI_POSTPONED, OI_CONTENTIOUS
from oi.helpers import OI_PRJ_DONE, OI_NO_EVAL, OI_ACCEPT_DELAY, OI_READ, OI_ANSWER, OI_WRITE, OI_ALL_PERMS, OI_CANCELLED_BID, OI_COM_ON_BID, OI_COMMISSION
from oi.helpers import SPEC_TYPES, SPOT_TYPES, NOTE_TYPE, TASK_TYPE, MESSAGE_TYPE, OIAction, ajax_login_required
from oi.projects.models import Project, Spec, Spot, Bid, PromotedProject, OINeedsPrjPerms
from oi.messages.models import Message
from oi.messages.templatetags.oifilters import oiescape, summarize

#    OIAction(func="moveProject", icon="moveprj.png", show=lambda project, user:project.has_perm(user, OI_WRITE) and project.bid_set.count()==0, title=_("Move the project")),

#def getprojects(request):
#    """Apply filter to project list"""
#    datemin = datetime.strptime(request.GET.get("datemin","2000,1,1"),"%Y,%m,%d")
#    datemax = datetime.strptime(request.GET.get("datemax","2100,1,1"),"%Y,%m,%d")
#    projects = Project.objects.filter(created__gte=datemin, created__lte=datemax, parent=None, public=True)
#    if request.GET.has_key("state"):
#        projects = projects.filter(state=request.GET["state"])

#    ancestors = [id for id in request.GET.get("categs","").split(",") if id!=""]
#    if ancestors:
#        projects = projects.filter(message__ancestors__in=ancestors)

#    promotedprj = PromotedProject.objects.filter(location="index")
#    return object_list(request, queryset=projects[:10], extra_context={'promotedprj': promotedprj})

@OINeedsPrjPerms(OI_READ, isajax=False)
def getproject(request, id, view="description"):
    if not view: view = "description"
    project = Project.objects.get(id=id)
    return direct_to_template(request, template="projects/project_detail.html", extra_context={'object': project, 'view':view, 'types':SPEC_TYPES, })

@OINeedsPrjPerms(OI_READ)
def listtasks(request, id):
    tasks = Project.objects.get(id=id).tasks.filter(Q(public=True)|Q(projectacl__user=request.user if request.user.is_authenticated() else None, projectacl__permission=OI_READ)).distinct().order_by('state', '-priority')
    return HttpResponse(serializers.oiserialize("json", tasks,
        extra_fields=("assignee.get_profile.get_display_name", "get_budget","allbid_sum","bid_set.count")))

@login_required
def editproject(request, id):
    """Shows the Edit template of the project"""
    project=None
    if id!='0':
        project = Project.objects.get(id=id)
        if not project.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden(_("Forbidden"))
    return direct_to_template(request, template='projects/editproject.html', extra_context={'user': request.user, 'parent':request.GET.get("parent"), 'project':project})

@login_required
def saveproject(request, id='0'):
    """Saves the edited project and redirects to it"""
    author=request.user
    parent = Project.objects.get(id=request.POST["parent"]) if request.POST.get("parent") else None
    if (parent and parent.state==OI_VALIDATED):
        return HttpResponse(_("Can not change a project already started"), status=431)
    
    if id=='0': #new project
        if not request.POST["title"]:
            return HttpResponse(_("Please enter a title"), status=531)
        project = Project(title = request.POST["title"], author=author, parent=parent)
    else: #existing project
        project = Project.objects.get(id=id)
        if not project.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden(_("Forbidden"))
        project.title = request.POST["title"]

    if request.POST.get("assignee") and len(request.POST["assignee"])>0:
        project.assignee = User.objects.get(username=request.POST["assignee"])
    else: #parent assignee by default
        if parent:
            project.assignee = parent.assignee
    for field in ["start_date","due_date","validaton","progress"]:
        if request.POST.has_key(field) and len(request.POST[field])>0:
            project.__setattr__(field, request.POST[field])
    project.state = OI_PROPOSED
    project.check_dates()
    project.save()
    
    # permission handling
    project.set_perm(author, OI_ALL_PERMS)
    project.inherit_perms()
    if project.assignee:
        project.apply_perm(project.assignee, OI_ALL_PERMS)
        
    #notify users about this project
    if project.parent:
        request.user.get_profile().notify_all(project.master, "new_project", project)
    #adds the project to user's observation
    request.user.get_profile().observed_projects.add(project.master)
    if request.POST.get("inline","0") == "1":
        return HttpResponse(serializers.serialize("json", [project]))
    else:
        return HttpResponseRedirect('/project/get/%s'%project.id)

@OINeedsPrjPerms(OI_WRITE)
def copyproject(request, id):
    """adds the given id to the project clipboard"""
    clipboard = request.session.get('project_clipboard',{})
    clipboard[id] = Project.objects.get(id=id).title
    request.session['project_clipboard'] = clipboard
    return HttpResponse(_("Project copied"))

def uncopyproject(request, id):
    """removes the given id from the project clipboard"""
    clipboard = request.session.get('project_clipboard',{})
    try:
        clipboard.pop(id)
    except KeyError:
        return HttpResponse(_("The project was not in the clipboard!"))
    request.session['project_clipboard'] = clipboard
    return HttpResponse(_("Project removed from clipboard"))

@OINeedsPrjPerms(OI_WRITE)
def pasteproject(request, id):
    """moves all task in clipboard as children of given project"""
    for taskid in request.session.get('project_clipboard',{}):
        task = Project.objects.get(id=taskid)
        task.parent_id = id
        task.save()
    request.session['project_clipboard'] = {}
    messages.info(request, _("Projects pasted"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_WRITE)
def editdate(request, id):
    """Modifies a date of the project"""
    project = Project.objects.get(id=id)
    if project.state == OI_STARTED and request.user == project.assignee and request.POST["field_name"]=="due_date": #The user is asking for more delay
        if project.bid_set.filter(rating__isnull=True): #if bidders, needs validation
            project.delay = request.POST["date"]
            project.save()
            #notify users about this project
            request.user.get_profile().notify_all(project, "project_modified", _("Request for delay"))            
            return HttpResponse(_("Request for delay awaiting validation"))
        else:
            project.due_date = request.POST["date"]
            project.check_dates()
            project.save()
            project.update_tree()
            return HttpResponse(_("Date updated"))
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a project already started"), status=431)

    project.__setattr__(request.POST["field_name"],request.POST["date"])
    project.check_dates()
    project.save()
    project.update_tree()
    
    #notify users about this project
    request.user.get_profile().notify_all(project, "project_modified", request.POST["date"])
    return HttpResponse(_("Date updated"))

@OINeedsPrjPerms(OI_WRITE)
def setpriority(request, id):
    """Sets the priority of the project"""
    project = Project.objects.get(id=id)
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a project already started"), status=431)
    project.priority = request.POST["priority"]
    project.save()
    return HttpResponse(_("Priority changed"))

@OINeedsPrjPerms(OI_WRITE)
def edittitle(request, id):
    """Modifies the title of the project"""
    project = Project.objects.get(id=id)
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a project already started"), status=431)

    project.title = request.POST["title"]
    project.save()
    
    #notify users about this project
    request.user.get_profile().notify_all(project, "project_modified", project.title)
    return HttpResponse(_("Title updated"))

@OINeedsPrjPerms(OI_READ)
@ajax_login_required
def offerproject(request, id):
    """Makes the current user assignee of the project"""
    project = Project.objects.get(id=id)
    if project.assignee and project.assignee != request.user:
        return HttpResponse(_("Project already assigned"))
    if project.state > OI_STARTED:
        return HttpResponse(_("Can not change a project already started"), status=431)

    project.assignee = request.user
    try:
        project.offer = Decimal("0"+request.POST.get("offer","0").replace(",","."))
    except InvalidOperation:
        return HttpResponse(_('Please enter a valid number'), status=531)
    project.commission = project.offer * OI_COMMISSION #computes project commission
    project.save()
    project.apply_perm(project.assignee, OI_ALL_PERMS)
    #adds the project to user's observation
    request.user.get_profile().observed_projects.add(project.master)

    project.switch_to(OI_ACCEPTED, request.user)
    messages.info(request, _("Project taken on"))
    return HttpResponse('', status=332)

@ajax_login_required
def delegateproject(request, id):
    """Offers delegation of the project to the specified user"""
    project = Project.objects.get(id=id)
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a project already started"), status=431)
    if project.assignee != request.user:
        return HttpResponse(_("Only the user in charge of the project can delegate it"))
    try:
        project.delegate_to = User.objects.get(username=request.POST["delegate_to"])
    except (KeyError, User.DoesNotExist):
        return HttpResponse(_("Cannot find user"), status=531)
    project.save()
    notification.send([project.delegate_to], "delegate", {'project':project}, True, request.user)
    return HttpResponse(_("Sent delegation offer"))

@ajax_login_required
def answerdelegate(request, id):
    """Accepts or rejects delegation of the project to the current user"""
    project = Project.objects.get(id=id)
    answer = request.POST["answer"]
    if project.delegate_to != request.user:
        return HttpResponse(_("The project was not delegated to you"))
    #notifies former assignee of the answer of the user
    notification.send([project.assignee], "answerdelegate", {'project':project, 'answer':answer}, True, request.user)
    project.delegate_to = None

    if answer == "true":
        project.assignee = request.user
        #adds the project to user's observation
        request.user.get_profile().observed_projects.add(project.master)
    project.save()
    return HttpResponse(_("reply sent"))

@ajax_login_required
def answerdelay(request, id):
    """Accepts or rejects the delay asked for the assignee"""
    project = Project.objects.get(id=id)
    answer = request.POST["answer"]
    if project.delay == None:
        return HttpResponse(_("No delay was requested"), status=531)

    # notifies the assignee
    notification.send([project.assignee], "answerdelay", {'project':project, 'answer':answer}, True, request.user)
    if answer == "false":
        project.reset_delay_request()
        return HttpResponse(_("The date was not changed"))
    if answer == "true":
        for bid in project.bid_set.filter(user=request.user):
            bid.rating = OI_ACCEPT_DELAY
            bid.save()
        if project.bid_set.filter(rating__isnull=True): #need more validation
            return HttpResponse(_("Awaiting other users' validation"))
            
        project.due_date = project.delay
        project.save()
        project.reset_delay_request()
        return HttpResponse(_("The date has been changed"))

    #if neither true nor false
    return HttpResponse(_("No reply received"), status=531)

@OINeedsPrjPerms(OI_READ)
@ajax_login_required
def bidproject(request, id):
    """Makes a new bid on the project"""
    project = Project.objects.get(id=id)
    try:
        amount = Decimal("0"+request.POST.get("bid","0").replace(",","."))
    except InvalidOperation:
        return HttpResponse(_("Invalid amount"))
    #checks that the user can afford the bid ; if not, redirects to the deposit page
    if amount > request.user.get_profile().balance:
        return HttpResponse('/user/myaccount#deposit/%s'%((amount-request.user.get_profile().balance).to_eng_string()),status=333)
    
    #and creates the bid
    bid, created = Bid.objects.get_or_create(project=project, user=request.user)
    bid.commission += amount * OI_COM_ON_BID #computes bid commission included in amount
    bid.amount += amount
    bid.save()
    
    #updates user account
    request.user.get_profile().make_payment(-(amount-bid.commission), _("Bid"), project)
    request.user.get_profile().make_payment(-bid.commission, _("Commission"), project)

    project.apply_perm(bid.user, OI_ALL_PERMS)
    #adds the project to user's observation
    request.user.get_profile().observed_projects.add(project.master)
    
    project.switch_to(OI_ACCEPTED, request.user)
    messages.info(request, ("Bid saved"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_READ)
def startproject(request, id):
    """Starts the project"""
    project = Project.objects.get(id=id)
    if not project.is_ready_to_start():
        return HttpResponse(_("Not enough bids"), status=531)
    if not project.switch_to(OI_STARTED, request.user):
        return HttpResponseForbidden(_("Only the assignee can start the project"))

    if not project.offer:
        project.offer = project.alloffer_sum() #sums up tasks offers if the project doesn't has one
        project.commission = project.allcommission_sum()
    project.delegate_to = None
    project.save()
    messages.info(request, _("Project started"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_WRITE)
def deliverproject(request, id):
    """Marks the project as delivered"""
    project = Project.objects.get(id=id)
    if not project.switch_to(OI_DELIVERED, request.user):
        return HttpResponseForbidden(_("only the assignee can deliver the project!"))

    project.progress = OI_PRJ_DONE
    #resets any delay demand
    project.reset_delay_request()
    messages.info(request, _("Project done!"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_READ)
def validateproject(request, id):
    """Validates the project by the user"""
    project = Project.objects.get(id=id)
    if project.state == OI_DELIVERED:
        for bid in project.bid_set.filter(user=request.user): #update user's bid
            bid.validated = True
            if request.user==project.assignee:
                bid.rating = OI_NO_EVAL # the assignee doesn't evaluates himself
            bid.save()
    if not project.switch_to(OI_VALIDATED, request.user):
        return HttpResponse(_("only bidders can validate the project!"))
    
    # pays the assignee
    project.assignee.get_profile().make_payment(project.offer or project.alloffer_sum(), _("Payment"), project)
#    request.user.get_profile().make_payment(-bid.commission, _("Commission"), project)
    messages.info(request, _("Validation saved"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_READ)
def evaluateproject(request, id):
    """Gives user's evaluation on the project"""
    project = Project.objects.get(id=id)
    rating = int(request.POST["rating"])
    comment = request.POST["comment"]
    if project.state == OI_VALIDATED:
        for bid in project.bid_set.filter(user=request.user):
            bid.rating = rating
            bid.comment = comment
            bid.save()
        #notify assignee that he has an evaluation
        notification.send([project.assignee], "project_eval", {'project':project, 'rating':rating}, True, request.user)
    messages.info(request, _("Evaluation saved"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_READ)
def cancelbid(request, id):
    """Cancels the bid of the user on the project given by id"""
    project = Project.objects.get(id=id)
    if project.state > OI_DELIVERED:
        return HttpResponse(_("The project is already over"))
    bids = project.bid_set.filter(user=request.user)
    if bids.count() < 1:
        return HttpResponse(_("You're not participating on this project"))
    for bid in bids:
        #If the project has not started, simply remove the bid and reimburses the user
        if project.state < OI_STARTED:
#            project.commission -= bid.amount*OI_COM_ON_BID #also reduce commission
            project.state = OI_ACCEPTED if project.is_ready_to_start() else OI_PROPOSED
            project.save()
            request.user.get_profile().make_payment(bid.amount, _("Bid cancelled"), bid.project)
            bid.delete()  
        else:        
            bid.rating = OI_CANCELLED_BID
            bid.validated = True #We won't ask for user's validation anymore
            bid.save()
    #notify users about this bid cancellation
    request.user.get_profile().notify_all(project, "project_bid_cancel", bid)
    messages.info(request, _("Bid cancelled"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_WRITE)
def answercancelbid(request, id):
    """Accepts or refuses bid cancellation"""
    project = Project.objects.get(id=id)
    bid = Bid.objects.get(id=request.POST["bid"])
    #Cancels the bid
    if request.POST.get("answer") == "true":
        bid.cancel()
        return HttpResponse(_("Bid cancelled"))
    if request.POST.get("answer") == "false":
        bid.rating = None
        bid.save()
        project.state = OI_CONTENTIOUS
        project.save()
        #alerts admins
        logging.getLogger("oi.alerts").error("Project %s has entered contentious state : http://www.openinitiative.com/project/get/%s"%(project.title, project.id))
        return HttpResponse(_("Cancelation refused. Awaiting decision"))
    #if neither true nor false
    return HttpResponse(_("No reply received"), status=531)

@OINeedsPrjPerms(OI_WRITE)
def cancelproject(request, id):
    """Cancels the project given by id"""
    project = Project.objects.get(id=id)
    if project.state > OI_DELIVERED:
        return HttpResponse(_("The project is already over"))
    if request.user != project.assignee:
        return HttpResponse(_("Only the user in charge of the project can cancel it"))
    #The assignee canceling the project after its start pays for the commission
    if project.state >= OI_STARTED:
        request.user.get_profile().make_payment(-project.commission, _("Commission"), project)
#        project.commission = 0
    project.state = OI_CANCELLED
    project.save()
    #notify users about this cancellation
    request.user.get_profile().notify_all(project, "project_cancel", project.title)
    return HttpResponse(_("Project cancelled. Awaiting confirmation from other users"))

@OINeedsPrjPerms(OI_READ)
def answercancelproject(request, id):
    """Accepts or refuses the cancellation of the project"""
    project = Project.objects.get(id=id)
    #if accepted, reimburses the bidder and deletes the bid
    if request.POST.get("answer") == "true":
        for bid in project.bid_set.filter(user=request.user):
            bid.cancel()
        return HttpResponse(_("Bid cancelled"))
    if request.POST.get("answer") == "false":
        project.state = OI_CONTENTIOUS
        project.save()
        #alerts admins
        logging.getLogger("oi.alerts").error("Project %s has entered contentious state : http://www.openinitiative.com/project/get/%s"%(project.title, project.id))
        return HttpResponse(_("Cancelation refused. Awaiting decision"))
    #if neither true nor false
    return HttpResponse(_("No reply received"), status=531)

@OINeedsPrjPerms(OI_WRITE)
def deleteproject(request, id):
    """Deletes the project given by id"""
    project = Project.objects.get(id=id)
    if project.bid_set.count() > 0:
        return HttpResponse(_("Can not delete a started project. Please stop it first."))
    if project.tasks.count() > 0:
        return HttpResponse(_("Can not delete a project containing tasks. Please delete all its tasks first."))
    
    project.delete()
    if project.parent:
        messages.info(request, _("The task has been deleted."))
        return HttpResponse('/project/get/%s'%(project.parent.id),status=333)
    else:
        messages.info(request, _("The project has been deleted."))
        return HttpResponse('/',status=333)

@OINeedsPrjPerms(OI_WRITE)
def moveproject(request, id):
    """Changes the parent of the project given by id"""
    project = Project.objects.get(id=id)
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a project already started"), status=431)
    project.parent = Project.objects.get(id=request.POST["parent"])
    project.save()
    messages.info(request, _("Project moved"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_WRITE)
def togglehideproject(request, id):
    """Makes the project private or public and outputs a message"""
    project = Project.objects.get(id=id)
    project.apply_public(not project.public)
    project.save()
    return HttpResponse(_("The project is now %s"%("public" if project.public else "private")))

@OINeedsPrjPerms(OI_WRITE)
def shareproject(request, id):
    """Shares the project with a user and outputs a message"""
    project = Project.objects.get(id=id)
    try:
        user = User.objects.get(username=request.POST["username"])
    except (KeyError, User.DoesNotExist):
        return HttpResponse(_("Cannot find user"), status=531)
    project.apply_perm(user, OI_ALL_PERMS)
    user.get_profile().observed_projects.add(project)
    messages.info(request, _("Project shared"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_WRITE)
def editprogress(request, id):
    """Updates the progress of the project"""
    project = Project.objects.get(id=id)
    if project.state != OI_STARTED:
        return HttpResponse(_("The project has to be started for the progress to be updated"))
    if request.user != project.assignee:
        return HttpResponse(_("Only the user in charge of can update its progress"))

    progress = request.POST.get("progress")
    if not progress:
        return HttpResponse(_("Invalid value"))
    project.progress = Decimal(progress) / 100
    project.save()
    #notify users about this state change
    request.user.get_profile().notify_all(project, "project_state", "%s %%"%project.progress)
    return HttpResponse(_("Progress updated"))

@ajax_login_required
@OINeedsPrjPerms(OI_READ)
def observeproject(request, id):
    """adds the project in the observe list of the user"""
    project = Project.objects.get(id=id)
    if request.POST.has_key("stop"):
        request.user.get_profile().observed_projects.remove(project)
        return HttpResponse(_("Stopped following the project"))
    else:
        request.user.get_profile().observed_projects.add(project)
        return HttpResponse(_("Project followed"))
    
@OINeedsPrjPerms(OI_WRITE)
def editspec(request, id, specid):
    """Edit template of a spec contains a spec details edit template"""
    spec=None
    if specid!='0':
        spec = Spec.objects.get(id=specid)
    extra_context = {'divid': request.GET["divid"], 'spec':spec, 'types':SPEC_TYPES, 'specorder':request.GET.get("specorder")}
    return object_detail(request, queryset=Project.objects, object_id=id, template_object_name='project', template_name='projects/spec/editspec.html', extra_context=extra_context)

@OINeedsPrjPerms(OI_WRITE)
def editspecdetails(request, id, specid):
    """Edit template of a spec detail, ie: text, image, file..."""
    divid = request.GET["divid"]
    type = int(request.GET["type"])
    project = Project.objects.get(id=id)
    spec=None
    if specid!='0':
        if project.state > OI_ACCEPTED:
            return HttpResponse(_("Can not change a project already started"), status=431)
        spec = Spec.objects.get(id=specid)
    return direct_to_template(request, template='projects/spec/edit_type%s.html'%(type), extra_context={'user': request.user, 'divid': divid, 'project':project, 'spec':spec})

@login_required
@OINeedsPrjPerms(OI_WRITE)
def savespec(request, id, specid='0'):
    """saves the spec"""
    project = Project.objects.get(id=id)
    
    order = int(request.POST["order"])
    if order==-1:
        order = project.get_max_order()+1
    else:
        if project.state > OI_ACCEPTED:
            return HttpResponse(_("Can not change a project already started"), status=431)
        project.insert_spec(order)
    
    if specid=='0': #new spec
        spec = Spec(text = oiescape(request.POST["text"]), author=request.user, project=project, order=order, type=int(request.POST["type"]))
    else: #edit existing spec
        spec = Spec.objects.get(id=specid)
        spec.text = request.POST.get("legend") or oiescape(request.POST["text"])
        
    if request.POST.has_key("url"):
        spec.url = request.POST["url"]
        
    filename = request.POST.get("filename")
    if filename:
#        filename = normalize("NFC", filename)
        filename = normalize("NFKD", filename).encode('ascii', 'ignore').replace('"', '')
        spec.file.delete()
        path = ("%s%s_%s_%s"%(TEMP_DIR,request.user.id,request.POST["ts"],filename))
        spec.file.save(filename, File(open(path)), False)
        os.remove(path)
    spec.save()

    #notify users about this spec change
    request.user.get_profile().notify_all(project, "project_spec", spec)
    return render_to_response('projects/spec/spec.html',{'user': request.user, 'project' : project, 'spec' : spec})

@OINeedsPrjPerms(OI_WRITE)
def deletespec(request, id, specid):
    """deletes the spec"""
    spec = get_object_or_404(Spec, id=specid)
    if spec.project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a project already started"), status=431)
    spec.delete()
    return HttpResponse(_("Specification deleted"))

@OINeedsPrjPerms(OI_WRITE)
def savespot(request, id, specid, spotid):
    """saves an annotation spot linked to a spec"""
    if spotid=="0":
        spot = Spot(spec = Spec.objects.get(id=specid))
    else:
        if spot.spec.project.id != int(id):
            return HttpResponse(_("Wrong arguments"), status=531)
        spot = Spot.objects.get(id=spotid)
    spot.offsetX = request.POST['x']
    spot.offsetY = request.POST['y']
    spot.task = Project.objects.get(id=request.POST['taskid'])
    spot.save()
    return HttpResponse(serializers.serialize("json", [spot]))
    
@OINeedsPrjPerms(OI_WRITE)
def removeSpot(request, id, specid, spotid):
    spot = Spot.objects.get(id=spotid)
    if spot.spec.id == int(specid) and spot.spec.project.id == int(id):
        spot.delete()
        return HttpResponse(_("Annotation removed"))
    else:
        return HttpResponse(_("Wrong arguments"), status=531)

@OINeedsPrjPerms(OI_WRITE)
def uploadfile(request, id, specid='0'):
    """temporarily stores a file to be used in a spec"""
    uploadedfile = request.FILES['file']
    divid = request.POST['divid']
    ts = int(time())
#    filename = normalize("NFC", uploadedfile.name).encode('utf-8').
    filename = normalize("NFKD", uploadedfile.name).encode('ascii', 'ignore').replace('"', '')
    tempfile = open("%s%s_%s_%s"%(TEMP_DIR,request.user.id,ts,filename), 'wb+')
    for chunk in uploadedfile.chunks():
        tempfile.write(chunk)
    tempfile.close()
    return render_to_response('projects/spec/fileframe.html',{'divid':divid,'filename':filename,'ts':ts,'projectid':id})

@OINeedsPrjPerms(OI_WRITE)
def deltmpfile(request, id):
    """deletes a temporary file"""
    path = "%s%s_%s_%s"%(TEMP_DIR,request.user.id,request.POST["ts"],request.POST["filename"])
    os.remove(path)
    return HttpResponse(_("File deleted"))

@OINeedsPrjPerms(OI_READ)
def getfile(request, id, filename):
    """gets a file in the FS for download"""
    response = HttpResponse(mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; '
#    response['X-Sendfile'] = "%sproject/%s/%s"%(MEDIA_ROOT,id,quote(filename.encode('utf8')))
    response['X-Sendfile'] = "%sproject/%s/%s"%(MEDIA_ROOT,id,filename.encode('utf8'))
    try:
        response['Content-Length'] = os.path.getsize("%sproject/%s/%s"%(MEDIA_ROOT,id,filename))
    except OSError:
        raise Http404
    return response
    
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
            obj.description += " - " + Project.objects.get(id=id).title
        return obj(request)

    def get_object(self, request, *args, **kwargs):
        if self.id=='0':
            return None
        else:
            return Project.objects.get(id=self.id)

    def items(self, obj):
        if obj:
            return obj.descendants.order_by('-created')[:20]
        else:
            return Project.objects.order_by('-created')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        desc = ""
        for spec in item.spec_set.all():
            desc += "\n- " + summarize(spec.text)
        return desc
        
    def item_link(self, item):
        return "/project/get/%s"%item.id
