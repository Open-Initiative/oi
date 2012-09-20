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
from django.utils.simplejson.encoder import JSONEncoder
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_detail, object_list
from django.views.generic.simple import direct_to_template
from oi.settings import MEDIA_ROOT, TEMP_DIR
from oi.helpers import OI_PRJ_STATES, OI_PROPOSED, OI_ACCEPTED, OI_STARTED, OI_DELIVERED, OI_VALIDATED, OI_CANCELLED, OI_POSTPONED, OI_CONTENTIOUS
from oi.helpers import OI_PRJ_DONE, OI_NO_EVAL, OI_ACCEPT_DELAY, OI_READ, OI_ANSWER, OI_BID, OI_MANAGE, OI_WRITE, OI_ALL_PERMS, OI_CANCELLED_BID, OI_COM_ON_BID, OI_COMMISSION
from oi.helpers import OI_PRJ_VIEWS, SPEC_TYPES, SPOT_TYPES, NOTE_TYPE, TASK_TYPE, MESSAGE_TYPE, OIAction, ajax_login_required
from oi.projects.models import Project, Spec, Spot, Bid, PromotedProject, OINeedsPrjPerms, Release
from oi.messages.models import Message
from oi.messages.templatetags.oifilters import oiescape, summarize
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
def getproject(request, id, view="overview"):
    if not view: view = "overview"
    project = Project.objects.get(id=id)
    return direct_to_template(request, template="projects/project_detail.html", extra_context={'object': project, 'current_view':view, 'views':OI_PRJ_VIEWS, 'types':SPEC_TYPES, })

@OINeedsPrjPerms(OI_READ)
def listtasks(request, id):
    """list tasks of requested projects in id or optionnal url parameter expand. Takes care of permissions and order"""
    lists = []
    #takes the given id as default if expand is not provided
    idlist = [id] if not request.GET.has_key("expand") else request.GET["expand"].split(",")
    for taskid in idlist:
        if taskid:
            project = Project.objects.get(id=taskid)
            #if user doesn't have permission to see the project, add it as '...'
            if project.parent and not project.has_perm(request.user, OI_READ):
                #adding the task if the user has no right on it, but with no info
                lists.append('[{"pk": %s, "fields": {"state": 4, "parent": "%s", "title": "..."}}]'%(project.id,project.parent.id))
        
            if request.GET.has_key("listall"):
                tasks = project.descendants
            else:
                tasks = project.tasks
            if not request.user.is_superuser: #filters on user permissions
                tasks = tasks.filter_perm(request.user, OI_READ)
            if request.GET.has_key("order"):
                tasks = tasks.order_by(request.GET['order'])
            else:
                tasks = tasks.order_by('-priority')
                
            if request.GET.has_key('page'):
                paginator = Paginator(tasks, 25, 0, True)
                page = request.GET.get('page')
                try:
                    tasks = paginator.page(page).object_list
                except PageNotAnInteger:
                    tasks = paginator.page(1).object_list
                except EmptyPage:
                    tasks = paginator.page(paginator.num_pages).object_list
                    
            if request.GET.get("release"):
                tasks = tasks.filter(target__name=request.GET['release'])
            
            #appends the serialized task list to the global list
            lists.append(serializers.oiserialize("json", tasks,
                extra_fields=("author.get_profile" ,"assignee.get_profile.get_display_name", "get_budget","allbid_sum","bid_set.count")))
    return HttpResponse(JSONEncoder().encode(lists)) #serializes the whole thing

@OINeedsPrjPerms(OI_MANAGE)
def addrelease(request, id):
    """Add a new release to the project"""
    if request.POST["release"] == "":
        return HttpResponse(_("Not empty release"))
    Release(name = request.POST["release"], project = Project.objects.get(id=id).master).save()
    return HttpResponse(_("New release added"))

@OINeedsPrjPerms(OI_MANAGE)
def changerelease(request, id):
    """Change the release"""
    
    release = Release.objects.get(name = request.POST["release"])
    if release.done == True:
        return HttpResponse(_("Already done"))
        
    #get the master id of the project    
    master = Project.objects.get(id=id)
    
    if not master.target:
        master.target = Release.objects.create(name = _("Initial release"), project = master)
        master.save()
    
    #make a filter on the descendant master project, and update them
    master.descendants.filter(state__gte = 4, target__isnull=True).update(target=master.target)
    master.descendants.filter(state__lt = 4, target = master.target).update(target=None)
    
    #make the old release done true
    master.target.done = True
    master.target = release
    master.target.save()
    
    return HttpResponse(_("Release changed"))
    
@login_required
def editproject(request, id):
    """Shows the Edit template of the project"""
    project=None
    if id!='0':
        project = Project.objects.get(id=id)
        if not project.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden(_("Forbidden"))
    return direct_to_template(request, template='projects/editproject.html', extra_context={'user': request.user, 'parent':request.GET.get("parent"), 'project':project})

@ajax_login_required(keep_field='title')
def saveproject(request, id='0'):
    """Saves the edited project and redirects to it"""
    author=request.user
    parent = Project.objects.get(id=request.POST["parent"]) if request.POST.get("parent") else None
    if (parent and parent.state==OI_VALIDATED):
        return HttpResponse(_("Can not change a task already started"), status=431)
    
    assignee = None
    if request.POST.get("assignee") and len(request.POST["assignee"])>0:
        assignee = User.objects.get(username=request.POST["assignee"])
        
    if id=='0': #new project
        if request.POST.get("title"):
            title = request.POST["title"]
        else:
            if request.session.get("title"):
                title = request.session['title']
                assignee = assignee or request.user
            else:
                return HttpResponse(_("Please enter a title"), status=531)
        if parent:
            parent.inc_tasks_priority(0)
            assignee = assignee or parent.assignee
        project = Project(title = title, author=author, parent=parent)
    else: #existing project
        project = Project.objects.get(id=id)
        if not project.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden(_("Forbidden"))
        project.title = request.POST["title"]

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
        project.apply_perm(project.assignee, OI_MANAGE)
    project.save()
        
    if assignee:
        project.assign_to(assignee)
    #notify users about this project
    project.notify_all(request.user, "new_project", "")
    #adds the project to user's observation
    request.user.get_profile().follow_project(project.parent or project)
    if request.POST.get("inline","0") == "1":
        return HttpResponse(serializers.serialize("json", [project]))
    else:
        return HttpResponseRedirect('/project/%s'%project.id)

@OINeedsPrjPerms(OI_MANAGE)
def editdate(request, id):
    """Modifies a date of the project"""
    project = Project.objects.get(id=id)
    if project.state == OI_STARTED and request.user == project.assignee and request.POST["field_name"]=="due_date": #The user is asking for more delay
        if project.bid_set.filter(rating__isnull=True): #if bidders, needs validation
            project.delay = request.POST["date"]
            project.save()
            #notify users about this project
            project.notify_all(request.user, "project_modified", _("Request for delay"))
            return HttpResponse(_("Request for delay awaiting validation"))
        else:
            project.due_date = request.POST["date"]
            project.check_dates()
            project.save()
            project.update_tree()
            return HttpResponse(_("Date updated"))
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a task already started"), status=431)

    project.__setattr__(request.POST["field_name"],request.POST["date"])
    project.check_dates()
    project.save()
    project.update_tree()
    
    #notify users about this project
    project.notify_all(request.user, "project_modified", request.POST["date"])
    return HttpResponse(_("Date updated"))

@OINeedsPrjPerms(OI_WRITE)
def setpriority(request, id):
    """Sets the priority of the project"""
    project = Project.objects.get(id=id)
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a task already started"), status=431)
    project.priority = request.POST["priority"]
    project.save()
    return HttpResponse(_("Priority changed"))

@OINeedsPrjPerms(OI_WRITE)
def edittitle(request, id):
    """Modifies the title of the project"""
    project = Project.objects.get(id=id)
    if project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a task already started"), status=431)

    project.title = request.POST["title"]
    project.save()
    
    #notify users about this project
    project.notify_all(request.user, "project_modified", project.title)
    return HttpResponse(_("Title updated"))

@OINeedsPrjPerms(OI_MANAGE)
@ajax_login_required
def offerproject(request, id):
    """Makes the current user assignee of the project"""
    project = Project.objects.get(id=id)
    if project.assignee and project.assignee != request.user:
        return HttpResponse(_("Task already assigned"))
    if project.state > OI_STARTED:
        return HttpResponse(_("Can not change a task already started"), status=431)
    
    if project.descendants.filter(offer__gt=0):   
        return HttpResponse(_("The task '%s' already has an offer"%project.descendants.filter(offer__gt=0)[0].title), status=431)
    elif project.ancestors.filter(offer__gt=0):
        return HttpResponse(_("The task '%s' already has an offer"%project.ancestors.filter(offer__gt=0)[0].title), status=431)

    project.assign_to(request.user)
    try:
        project.offer = Decimal("0"+request.POST.get("offer","0").replace(",","."))
    except InvalidOperation:
        return HttpResponse(_('Please enter a valid number'), status=531)
    project.commission = project.offer * OI_COMMISSION #computes project commission
    project.save()
    project.apply_perm(project.assignee, OI_WRITE)
    #adds the project to user's observation
    request.user.get_profile().follow_project(project.master)

    project.switch_to(OI_ACCEPTED, request.user)
    messages.info(request, _("Task taken on"))
    return HttpResponse('', status=332)

@ajax_login_required
@OINeedsPrjPerms(OI_MANAGE)
def delegateproject(request, id):
    """Offers delegation of the project to the specified user"""
    project = Project.objects.get(id=id)
    if project.state > OI_STARTED:
        return HttpResponse(_("Can not change a task already started"), status=431)
    if project.assignee != request.user:
        return HttpResponse(_("Only the user in charge of the project can delegate it"))
    try:
        project.delegate_to = User.objects.get(username=request.POST["delegate_to"])
    except (KeyError, User.DoesNotExist):
        return HttpResponse(_("Cannot find user"), status=531)
    project.save()
    project.delegate_to.get_profile().get_default_observer(project).notify("delegate", project=project, sender=request.user)
    return HttpResponse(_("Sent delegation offer"))

@ajax_login_required
@OINeedsPrjPerms(OI_READ)
def answerdelegate(request, id):
    """Accepts or rejects delegation of the project to the current user"""
    project = Project.objects.get(id=id)
    answer = request.POST["answer"]
    if project.delegate_to != request.user:
        return HttpResponse(_("The project was not delegated to you"))
    project.delegate_to = None
    #notifies former assignee of the answer of the user BEFORE we lose info
    project.assignee.get_profile().get_default_observer(project).notify("answerdelegate", project=project, param=answer, sender=request.user)

    if answer == "true":
        #former assignee now has to validate
        bid, created = Bid.objects.get_or_create(project=project, user=project.assignee)
        project.assign_to(request.user)
        project.apply_perm(request.user, OI_MANAGE)
        #adds the project to user's observation
        request.user.get_profile().follow_project(project.master)
    project.save()
    return HttpResponse(_("reply sent"))

@ajax_login_required
@OINeedsPrjPerms(OI_READ)
def answerdelay(request, id):
    """Accepts or rejects the delay asked for the assignee"""
    project = Project.objects.get(id=id)
    answer = request.POST["answer"]
    if project.delay == None:
        return HttpResponse(_("No delay was requested"), status=531)

    # notifies the assignee
    project.assignee.get_profile().get_default_observer(project).notify("answerdelay", project=project, param=answer, sender=request.user)
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

@OINeedsPrjPerms(OI_BID)
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

    #adds the project to user's observation
    request.user.get_profile().follow_project(project.master)
    
    project.switch_to(OI_ACCEPTED, request.user)
    #notify users about this bid
    project.notify_all(request.user, "project_bid", bid)
    messages.info(request, _("Bid saved"))
    return HttpResponse('', status=332)
    
@OINeedsPrjPerms(OI_READ)
def validatorproject(request, id):
    """Add the user as a validator"""
    project = Project.objects.get(id=id)
    
    try:
        user = User.objects.get(username=request.POST["username"])
    except (KeyError, User.DoesNotExist):
        return HttpResponse(_("Cannot find user"), status=531)
    
    bid, created = Bid.objects.get_or_create(project=project, user=user)
    
    project.apply_perm(user, OI_BID)
    user.get_profile().follow_project(project.master)
    user.get_profile().get_default_observer(project).notify("share", project=project, sender=request.user)
    return HttpResponse(_("The user has been added as a validator"))

@ajax_login_required
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
    messages.info(request, _("Task started"))
    return HttpResponse('', status=332)

@ajax_login_required
def deliverproject(request, id):
    """Marks the project as delivered"""
    project = Project.objects.get(id=id)
    if not project.switch_to(OI_DELIVERED, request.user):
        return HttpResponseForbidden(_("only the assignee can deliver the project!"))
        
    project.progress = OI_PRJ_DONE
    #resets any delay demand
    project.reset_delay_request()
    messages.info(request, _("Task done!"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_BID)
def validateproject(request, id):
    """Validates the project by the user"""
    project = Project.objects.get(id=id)
    if project.state == OI_DELIVERED:
        for bid in project.bid_set.filter(user=request.user): #update user's bid
            if bid.validated:
                return HttpResponseForbidden(_("already validated!"))
            bid.validated = True
            bid.save()
    if not project.switch_to(OI_VALIDATED, request.user):
        return HttpResponse(_("only bidders can validate the project!"))
    
    if request.user==project.assignee:
        bid.rating = OI_NO_EVAL # the assignee doesn't evaluates himself
        bid.save()
    # pays the assignee
    project.assignee.get_profile().make_payment(bid.amount - bid.commission, _("Payment"), project)
#    request.user.get_profile().make_payment(-bid.commission, _("Commission"), project)
    messages.info(request, _("Validation saved"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_BID)
def evaluateproject(request, id):
    """Gives user's evaluation on the project"""
    project = Project.objects.get(id=id)
    rating = int(request.POST["rating"])
    comment = request.POST["comment"]
    if request.user == project.assignee:
        return HttpResponse(_("You can not evaluate yourself"), status=433)
    if project.state == OI_VALIDATED:
        for bid in project.bid_set.filter(user=request.user):
            if bid.rating is not None:
                return HttpResponse(_("You have already evaluated this task"), status=433)
            bid.rating = rating
            bid.comment = comment
            bid.save()
        #notify assignee that he has an evaluation
        project.assignee.get_profile().get_default_observer(project).notify("project_eval", project=project, param=unicode(rating), sender=request.user)
    messages.info(request, _("Evaluation saved"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_BID)
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
    project.notify_all(request.user, "project_bid_cancel", bid)
    messages.info(request, _("Bid cancelled"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_READ)
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
        logging.getLogger("oi.alerts").error("Task %s has entered contentious state : http://www.openinitiative.com/project/%s"%(project.title, project.id))
        return HttpResponse(_("Cancelation refused. Awaiting decision"))
    #if neither true nor false
    return HttpResponse(_("No reply received"), status=531)

@OINeedsPrjPerms(OI_MANAGE)
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
    project.notify_all(request.user, "project_cancel", project.title)
    return HttpResponse(_("Task cancelled. Awaiting confirmation from other users"))

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
        logging.getLogger("oi.alerts").error("Task %s has entered contentious state : http://www.openinitiative.com/project/%s"%(project.title, project.id))
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
        return HttpResponse('/project/%s'%(project.parent.id),status=333)
    else:
        messages.info(request, _("The project has been deleted."))
        return HttpResponse('/',status=333)

@OINeedsPrjPerms(OI_WRITE)
def moveproject(request, id):
    """Changes the parent of the project given by id"""
    project = Project.objects.get(id=id)
    parent = Project.objects.get(id=request.POST["parent"])
    priority = Project.objects.get(id=request.POST["after"]).priority if request.POST.has_key("after") else 0
    if project.state > OI_ACCEPTED or parent.state > OI_STARTED:
        return HttpResponse(_("Can not change a task already started"), status=431)
    if project==parent or project in parent.ancestors.all():
        return HttpResponse(_("Can not move a task inside itself"), status=531)
    project.parent = parent
    parent.inc_tasks_priority(priority)
    project.priority = priority
    project.save()
    for task in project.descendants.all():
        task.save() #recompute ancestors
    return HttpResponse(_("Task moved"))

@OINeedsPrjPerms(OI_MANAGE)
def togglehideproject(request, id):
    """Makes the project private or public and outputs a message"""
    project = Project.objects.get(id=id)
    project.apply_public(not project.public)
    project.save()
    return HttpResponse(_("The task is now %s"%("public" if project.public else "private")))

@OINeedsPrjPerms(OI_MANAGE)
def shareproject(request, id):
    """Shares the project with a user and outputs a message"""
    project = Project.objects.get(id=id)
    try:
        user = User.objects.get(username=request.POST["username"])
    except (KeyError, User.DoesNotExist):
        return HttpResponse(_("Cannot find user"), status=531)
    project.apply_perm(user, OI_BID)
    project.apply_perm(user, OI_READ)
    user.get_profile().follow_project(project)
    user.get_profile().get_default_observer(project).notify("share", project=project, sender=request.user)
    messages.info(request, _("Task shared"))
    return HttpResponse('', status=332)

@OINeedsPrjPerms(OI_MANAGE)
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
    project.progress = int(progress)
    project.save()
    #notify users about this state change
    project.notify_all(request.user, "project_state", "%s %%"%project.progress)
    return HttpResponse(_("Progress updated"))

@ajax_login_required
@OINeedsPrjPerms(OI_READ)
def favproject(request, id):
    """adds the project in the observe list of the user"""
    project = Project.objects.get(id=id)
    if request.POST.has_key("stop"):
        request.user.get_profile().unfollow_project(project)
        return HttpResponse(False)
    else:
        request.user.get_profile().follow_project(project)
        return HttpResponse(True)
    
@OINeedsPrjPerms(OI_WRITE)
def editspec(request, id, specid):
    """Edit template of a spec contains a spec details edit template"""
    spec=None
    order = request.GET.get("specorder")
    if specid!='0':
        spec = Spec.objects.get(id=specid)
        if spec.project.id != int(id):
            return HttpResponse(_("Wrong arguments"), status=531)
        order = spec.order
    extra_context = {'divid': request.GET["divid"], 'spec':spec, 'types':SPEC_TYPES, 'specorder':order}
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
            return HttpResponse(_("Can not change a task already started"), status=431)
        spec = Spec.objects.get(id=specid)
        if spec.project.id != int(id):
            return HttpResponse(_("Wrong arguments"), status=531)
    return direct_to_template(request, template='projects/spec/edit_type%s.html'%(type), extra_context={'user': request.user, 'divid': divid, 'project':project, 'spec':spec})

@login_required
@OINeedsPrjPerms(OI_WRITE)
def savespec(request, id, specid='0'):
    """saves the spec"""
    project = Project.objects.get(id=id)
    order = int(request.POST.get("order", -1))
    if order==-1:
        order = project.get_max_order()+1
    else:
        if project.state > OI_ACCEPTED:
            return HttpResponse(_("Can not change a task already started"), status=431)
        project.insert_spec(order)
    
    if specid=='0': #new spec
        spec = Spec(text = oiescape(request.POST["text"]), author=request.user, project=project, order=order, type=1)
    else: #edit existing spec
        spec = Spec.objects.get(id=specid)
        if spec.project.id != int(id):
            return HttpResponse(_("Wrong arguments"), status=531)
        spec.text = request.POST.get("legend") or oiescape(request.POST["text"])
        
    if request.POST.has_key("url"):
        spec.url = request.POST["url"]
    if request.POST.has_key("type"):
        spec.type = int(request.POST["type"])
    
    filename = request.POST.get("filename")
    if not filename and not spec.file and spec.type in (2,5):
        return HttpResponse(_("Wrong arguments"), status=531)
    if filename:
#        filename = normalize("NFC", filename)
        filename = normalize("NFKD", filename).encode('ascii', 'ignore').replace('"', '')
        if spec.file:
            spec.file.delete()
        path = ("%s%s_%s_%s"%(TEMP_DIR,request.user.id,request.POST["ts"],filename))
        spec.file.save(filename, File(open(path)), False)
        os.remove(path)
    spec.save()

    #notify users about this spec change
    project.notify_all(request.user, "project_spec", spec.text)
    return render_to_response('projects/spec/spec.html',{'user': request.user, 'project' : project, 'spec' : spec})

@OINeedsPrjPerms(OI_WRITE)
def movespec(request, id, specid):
    """Move template of an oderspec to an other spec order"""
    spec = Spec.objects.get(id=specid)
    if spec.project.id != int(id):
        return HttpResponse(_("Wrong arguments"), status=531)
    if not request.POST.get("target"):
        return HttpResponse(_("Wrong arguments"), status=531)
    target = Spec.objects.get(id=request.POST["target"]) 
    if not (target.project.id == int(id) and spec.project.id == int(id)):
        return HttpResponse(_("Wrong arguments"), status=531)
    spec.order,target.order = target.order,spec.order
    spec.save()
    target.save()
    return HttpResponse(_("Spec moved"))

@OINeedsPrjPerms(OI_WRITE)
def deletespec(request, id, specid):
    """deletes the spec"""
    spec = get_object_or_404(Spec, id=specid)
    if spec.project.id != int(id):
        return HttpResponse(_("Wrong arguments"), status=531)
    if spec.project.state > OI_ACCEPTED:
        return HttpResponse(_("Can not change a task already started"), status=431)
    spec.delete()
    return HttpResponse(_("Specification deleted"))

@OINeedsPrjPerms(OI_WRITE)
def savespot(request, id, specid, spotid):
    """saves an annotation spot linked to a spec"""
    spec = Spec.objects.get(id=specid)
    if spotid=="0": #new spot
        spot = Spot(spec = Spec.objects.get(id=specid))
        if spot.spec.project.id != int(id) or spot.spec.project.id != spec.project.id:
            return HttpResponse(_("Wrong arguments"), status=531)
    else:
        spot = Spot.objects.get(id=spotid)
        if spot.spec.project.id != int(id) or spot.spec.project.id != spec.project.id:
            return HttpResponse(_("Wrong arguments"), status=531)
    
    spot.offsetX = request.POST['x']
    spot.offsetY = request.POST['y']
    spot.task = Project.objects.get(id=request.POST['taskid'])
    spot.save()
    return HttpResponse(serializers.serialize("json", [spot]))
    
@OINeedsPrjPerms(OI_WRITE)
def removeSpot(request, id, specid, spotid):
    spot = Spot.objects.get(id=spotid)
    if spot.spec.id == int(specid) and spot.spec.project.id == int(id):
        if spot.task and spot.task.spot_set.count()==1:
            spot.task.delete()
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
        return "/project/%s"%item.id
