#coding: utf-8
# Vues des projets
import os
import logging
from time import time
from datetime import datetime,timedelta
from decimal import Decimal, InvalidOperation
from urllib import quote
from django.core import serializers
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_detail, object_list
from django.views.generic.simple import direct_to_template
from oi.notification import models as notification
from oi.settings import MEDIA_ROOT, TEMP_DIR
from oi.helpers import OI_PRJ_STATES, OI_PROPOSED, OI_ACCEPTED, OI_STARTED, OI_DELIVERED, OI_VALIDATED, OI_CANCELLED, OI_POSTPONED, OI_CONTENTIOUS
from oi.helpers import OI_PRJ_DONE, OI_NO_EVAL, OI_ACCEPT_DELAY, OI_READ, OI_ANSWER, OI_WRITE, OI_ALL_PERMS, OI_CANCELLED_BID, OI_COM_ON_BID
from oi.helpers import SPEC_TYPES, OIAction, ajax_login_required
from oi.projects.models import Project, Spec, Bid, PromotedProject, OINeedsPrjPerms
from oi.messages.models import Message
from oi.messages.templatetags.oifilters import oiescape

OIPrjActions = [
    OIAction(func="startProject", icon="startprj.png", show=lambda project, user:project.state == 1 and project.assignee == user, title=_("Start the project")),
    OIAction(func="deliverProject", icon="okprj.png", show=lambda project, user:project.state == 2 and project.assignee == user, title=_("Mark the project as done")),
    OIAction(func="validateProject", icon="okprj.png", show=lambda project, user:project.state == 3 and project.is_bidder(user), title=_("Confirm the project end")),
    OIAction(func="evalProject", icon="evalprj.png", show=lambda project, user:project.state == 4 and project.is_bidder(user), title=_("Evaluate the project")),
    OIAction(func="hideProject", icon="privateprj.png", show=lambda project, user:project.has_perm(user, OI_WRITE) and project.public, title=_("Make the project private")),
    OIAction(func="shareProject", icon="shareprj.png", show=lambda project, user:project.has_perm(user, OI_WRITE) and not project.public, title=_("Share the project")),
    OIAction(func="deleteProject", icon="delprj.png", show=lambda project, user:project.has_perm(user, OI_WRITE) and project.bid_set.count()==0 and project.tasks.count()==0, title=_("Delete the project")),
    OIAction(func="moveProject", icon="moveprj.png", show=lambda project, user:project.has_perm(user, OI_WRITE) and project.bid_set.count()==0, title=_("Move the project")),
    OIAction(func="cancelProject", icon="delprj.png", show=lambda project, user:project.has_perm(user, OI_WRITE) and project.bid_set.count()>0 and project.state <= 1 and user==project.assignee, extra_param="false", title=_("Cancel the project")),
    OIAction(func="cancelProject", icon="delprj.png", show=lambda project, user:project.has_perm(user, OI_WRITE) and project.bid_set.count()>0 and (project.state == 2 or project.state == 3) and user==project.assignee, extra_param="true", title=_("Cancel the project")),

    OIAction(func="observeProject", icon="favprj.png", title=_("Follow the projet"))]

def getprojects(request):
    """Apply filter to project list"""
    datemin = datetime.strptime(request.GET.get("datemin","2000,1,1"),"%Y,%m,%d")
    datemax = datetime.strptime(request.GET.get("datemax","2100,1,1"),"%Y,%m,%d")
    projects = Project.objects.filter(created__gte=datemin, created__lte=datemax, parent=None, public=True)
    if request.GET.has_key("state"):
        projects = projects.filter(state=request.GET["state"])

    ancestors = [id for id in request.GET.get("categs","").split(",") if id!=""]
    if ancestors:
        projects = projects.filter(message__ancestors__in=ancestors)

    promotedprj = PromotedProject.objects.filter(location="index")
    return object_list(request, queryset=projects[:10], extra_context={'promotedprj': promotedprj})

@OINeedsPrjPerms(OI_READ)
def getproject(request, id, view="description"):
    if not view: view = "description"
    project = Project.objects.get(id=id)
    actions = filter(lambda a:a.show(project, request.user), OIPrjActions)
    return direct_to_template(request, template="projects/project_detail.html", extra_context={'object': project, 'actions': actions, 'view':view})

@OINeedsPrjPerms(OI_READ)
def listtasks(request, id):
    tasks = Project.objects.get(id=id).tasks.order_by('state')
    return HttpResponse(serializers.serialize("json", tasks))

@login_required
def editproject(request, id):
    """Shows the Edit template of the project"""
    project=None
    if id!='0':
        project = Project.objects.get(id=id)
        if not project.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden(_("Forbidden"))
    return direct_to_template(request, template='projects/editproject.html', extra_context={'user': request.user, 'parent':request.GET.get("parent"), 'project':project})
    # 'message':request.GET.get("message"),

@login_required
def saveproject(request, id='0'):
    """Saves the edited project and redirects to it"""
    author=request.user
    
    if id=='0': #new project
        #gets message from parent
#        if request.POST.has_key("parent"):
        if not request.POST["title"]:
            return HttpResponse(_("Please enter a title"), status=531)
        parent = Project.objects.get(id=request.POST["parent"]) if request.POST.get("parent") else None
#            message = parent.message
        #or from query
#        else:
#            message = Message.objects.get(id=request.POST["message"])
#        if not message.has_perm(request.user, OI_ANSWER):
#            return HttpResponseForbidden(_("Forbidden"))
        project = Project(title = request.POST["title"], author=author, parent=parent, public=True, state=OI_PROPOSED)
#        , message=message
        
    else: #existing project ####DEPRECATED?
        project = Project.objects.get(id=id)
        if not project.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden(_("Forbidden"))
        project.title = request.POST["title"]

    if request.POST.get("assignee") and len(request.POST["assignee"])>0:
        project.assignee = User.objects.get(username=request.POST["assignee"])
    if request.POST.has_key("start_date") and len(request.POST["start_date"])>0:
        project.start_date = request.POST["start_date"]
    if request.POST.has_key("due_date") and len(request.POST["due_date"])>0:
        project.due_date = request.POST["due_date"]
    if request.POST.has_key("progress") and len(request.POST["progress"])>0:
        project.progress = request.POST["progress"]

    project.save()
    project.set_perm(author, OI_ALL_PERMS)
    if project.assignee:
        project.set_perm(project.assignee, OI_ALL_PERMS)
        
    #notify users about this project
#    request.user.get_profile().msg_notify_all(project.message, "new_project", project)
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
        if project.bid_set.filter(rating__isnull=True): #needs validation
            project.delay = request.POST["date"]
            project.save()
            #notify users about this project
            request.user.get_profile().notify_all(project, "project_modified", _("Request for delay"))            
            return HttpResponse(_("Request for delay awaiting validation"))
        else:
            project.due_date = request.POST["date"]
            project.save()
            return HttpResponse(_("Date updated"))
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a project already started"))

    project.__setattr__(request.POST["field_name"],request.POST["date"])
    project.save()
    
    #notify users about this project
    request.user.get_profile().notify_all(project, "project_modified", request.POST["date"])
    return HttpResponse(_("Date updated"))

@OINeedsPrjPerms(OI_WRITE)
def setpriority(request, id):
    """Sets the priority of the project"""
    project = Project.objects.get(id=id)
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a project already started"))
    project.priority = request.POST["priority"]
    project.save()
    return HttpResponse(_("Priority changed"))

@OINeedsPrjPerms(OI_WRITE)
def edittitle(request, id):
    """Modifies the title of the project"""
    project = Project.objects.get(id=id)
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a project already started"))

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

    project.assignee = request.user
    project.offer = Decimal("0"+request.POST.get("offer","0").replace(",","."))
    project.save()
    project.set_perm(project.assignee, OI_ALL_PERMS)

    if project.is_ready_to_start():
        project.state = OI_ACCEPTED
        project.save()
    
    #adds the project to user's observation
    request.user.get_profile().observed_projects.add(project.master)
    #notify users about this project
    request.user.get_profile().notify_all(project, "project_modified", project.state)
    messages.info(request, _("Project taken on"))
    return HttpResponse('', status=332)

@ajax_login_required
def delegateproject(request, id):
    """Offers delegation of the project to the specified user"""
    project = Project.objects.get(id=id)
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a project already started"))
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
        return HttpResponse(_("No delay was requested"))

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
    return HttpResponse(_("No reply received"))

@OINeedsPrjPerms(OI_READ)
@ajax_login_required
def bidproject(request, id):
    """Makes a new bid on the project"""
    project = Project.objects.get(id=id)
    try:
        amount = Decimal("0"+request.POST.get("bid","0").replace(",","."))
    except InvalidOperation:
        return HttpResponse(_("Invalid amount"))
    #checks that the user can afford the bid
    if amount > request.user.get_profile().balance:
        return HttpResponse('/user/myaccount#deposit/%s'%((amount-request.user.get_profile().balance).to_eng_string()),status=333)
    #updates user account
    request.user.get_profile().make_payment(-amount, _("Bid"), project)
    #and creates the bid
    bid, created = Bid.objects.get_or_create(project=project, user=request.user)
    bid.amount += amount
    bid.save()
    project.set_perm(bid.user, OI_ALL_PERMS)
    if project.is_ready_to_start():
        project.state = OI_ACCEPTED
    project.commission += bid.amount * OI_COM_ON_BID #computes project commission from bids
    project.save()
    
    #adds the project to user's observation
    request.user.get_profile().observed_projects.add(project.master)
    #notify users about this new bid
    request.user.get_profile().notify_all(project, "project_bid", bid)
    messages.info(request, ("Bid saved"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_READ)
def startproject(request, id):
    """Starts the project"""
    project = Project.objects.get(id=id)
    if project.state == OI_ACCEPTED:
        # only the assignee can start the project
        if project.assignee == request.user:
            project.state = OI_STARTED
            project.start_date = datetime.now()
            project.delegate_to = None
            project.save()
            #notify users about this state change
            request.user.get_profile().notify_all(project, "project_state", OI_PRJ_STATES[project.state][1])
    messages.info(request, _("Project started"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_WRITE)
def deliverproject(request, id):
    """Marks the project as delivered"""
    project = Project.objects.get(id=id)
    if project.state != OI_STARTED or project.assignee != request.user:
        return HttpResponse(_("only the assignee can deliver the project!"))
    project.progress = OI_PRJ_DONE
    if project.bid_set.all():
        project.state = OI_DELIVERED
    else: #if there aren't any bids, then the project is VALIDATED
        project.state = OI_VALIDATED

    project.due_date = datetime.now()
    project.save()
    #resets any delay demand
    project.reset_delay_request()
    #notify users about this state change
    request.user.get_profile().notify_all(project, "project_state", OI_PRJ_STATES[project.state][1])
    messages.info(request, _("Project done!"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_READ)
def validateproject(request, id):
    """Validates the project by the user"""
    project = Project.objects.get(id=id)
    if project.state == OI_DELIVERED:
        for bid in project.bid_set.filter(user=request.user):
            bid.validated = True
            if request.user==project.assignee:
                bid.rating = OI_NO_EVAL # the assignee doesn't evaluates himself
            bid.save()
        # If there are no more users waiting for validation
        if project.bid_set.filter(validated=False).count()==0:
            project.state = OI_VALIDATED
            # pays the assignee, deducts the commission
            project.assignee.get_profile().make_payment(project.bid_sum(), _("Payment"), project)
            project.assignee.get_profile().make_payment(-project.commission, _("Commission"), project)
            project.save()

            #notify users about this state change
            request.user.get_profile().notify_all(project, "project_state", OI_PRJ_STATES[project.state][1])
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
            project.commission -= bid.amount*OI_COM_ON_BID #also reduce commission
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
    return HttpResponse(_("No reply received"))

@OINeedsPrjPerms(OI_WRITE)
def cancelproject(request, id):
    """Cancels the project given by id"""
    project = Project.objects.get(id=id)
    if project.state > OI_DELIVERED:
        return HttpResponse(_("The project is already over"))
    if request.user != project.assignee:
        return HttpResponse(_("Only the user in charge of the project can cancel it"))
    project.state = OI_CANCELLED
    #The assignee canceling the project after its start pays for the commission
    if project.state > OI_STARTED:
        request.user.get_profile().make_payment(-project.commission, _("Commission"), project)
        project.commission = 0
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
    return HttpResponse(_("No reply received"))

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
        return HttpResponse(_("Can not change a project already started"))
    project.parent = Project.objects.get(id=request.POST["parent"])
    project.save()
    messages.info(request, _("Project moved"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_WRITE)
def hideproject(request, id):
    """Makes the project private and outputs a message"""
    project = Project.objects.get(id=id)
    project.public = False
    project.save()
    return HttpResponse(_("The project is now private"))

@OINeedsPrjPerms(OI_WRITE)
def shareproject(request, id):
    """Shares the project with a user and outputs a message"""
    project = Project.objects.get(id=id)
    user = User.objects.get(username=request.POST["username"])
    project.set_perm(user, OI_ALL_PERMS)
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
        request.user.get_profile().observed_projects.remove(project.master)
        return HttpResponse(_("Stopped following the project"))
    else:
        request.user.get_profile().observed_projects.add(project.master)
        return HttpResponse(_("Project followed"))
    
@OINeedsPrjPerms(OI_READ)
def projectview(request, id):
    """Shows the project summary"""
    project = Project.objects.get(id=id)
    #list the days covered by the project, for display
    days = []
    width = int(request.GET.get("width", "1"))
    if project.start_date and project.due_date:
        days = [project.start_date+timedelta(n*width) for n in range((project.due_date-project.start_date).days/width+1)]
    return render_to_response('projects/gantt/prjview.html',{'user':request.user, 'project':project, 'days':days, 'day_length':1./width})

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
            return HttpResponse(_("Can not change a project already started"))
        spec = Spec.objects.get(id=specid)
    return direct_to_template(request, template='projects/spec/edit_type%s.html'%(type), extra_context={'user': request.user, 'divid': divid, 'project':project, 'spec':spec})

@login_required
@OINeedsPrjPerms(OI_WRITE)
def savespec(request, id, specid='0'):
    """saves the spec"""
    author=request.user
    project = Project.objects.get(id=id)
    
    order = int(request.POST["order"])
    if order==-1:
        order = project.get_max_order()+1
    else:
        if project.state > OI_ACCEPTED:
            return HttpResponse(_("Can not change a project already started"))
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

    #notify users about this spec change
    request.user.get_profile().notify_all(project, "project_spec", spec)
    return render_to_response('projects/spec/spec.html',{'user': request.user, 'project' : project, 'spec' : spec})

@OINeedsPrjPerms(OI_WRITE)
def deletespec(request, id, specid):
    """deletes the spec"""
    spec = Spec.objects.get(id=specid)
    if spec.project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a project already started"))
    spec.delete()
    return HttpResponse(_("Specification deleted"))
    
@OINeedsPrjPerms(OI_WRITE)
def uploadfile(request, id, specid='0'):
    """temporarily stores a file to be used in a spec"""
    uploadedfile = request.FILES['file']
    divid = request.POST['divid']
    ts = int(time())
    tempfile = open("%s%s_%s_%s"%(TEMP_DIR,request.user.id,ts,uploadedfile.name), 'wb+')
    for chunk in uploadedfile.chunks():
        tempfile.write(chunk)
    tempfile.close()
    return render_to_response('projects/spec/fileframe.html',{'divid':divid,'filename':uploadedfile.name,'ts':ts,'projectid':id})

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
    response['Content-Disposition'] = 'attachment; filename=%s'%filename
    response['X-Sendfile'] = "%sproject/%s/%s"%(MEDIA_ROOT,id,filename)
    try:
        response['Content-Length'] = os.path.getsize("%sproject/%s/%s"%(MEDIA_ROOT,id,filename))
    except OSError:
        raise Http404
    return response
