#coding: utf-8
# Vues des projets
from random import random
import os
import logging
from time import time
from datetime import datetime,timedelta
from decimal import Decimal, InvalidOperation
from github import Github
from urllib import quote, urlencode
from urllib2 import Request, urlopen
from unicodedata import normalize
from django.core import serializers
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.contrib.sites.models import get_current_site
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.simplejson import JSONEncoder, JSONDecoder
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list_detail import object_detail, object_list
from django.views.generic.simple import direct_to_template
from oi.settings import MEDIA_ROOT, TEMP_DIR, github_id, github_secret
from oi.helpers import OI_PRJ_STATES, OI_PROPOSED, OI_ACCEPTED, OI_STARTED, OI_DELIVERED, OI_VALIDATED, OI_CANCELLED, OI_POSTPONED, OI_CONTENTIOUS, OI_TABLE_OVERVIEW
from oi.helpers import OI_PRJ_DONE, OI_NO_EVAL, OI_ACCEPT_DELAY, OI_READ, OI_ANSWER, OI_BID, OI_MANAGE, OI_WRITE, OI_ALL_PERMS, OI_CANCELLED_BID, OI_COM_ON_BID, OI_COMMISSION
from oi.helpers import OI_PRJ_VIEWS, SPEC_TYPES, OIAction, ajax_login_required
from oi.projects.models import Project, Spec, Spot, Bid, PromotedProject, OINeedsPrjPerms, Release, GitHubSync, Reward, RewardForm
from oi.messages.models import Message
from oi.messages.templatetags.oifilters import oiescape, summarize
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

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
    return direct_to_template(request, template="projects/project_detail.html", extra_context={'object': project, 'current_view':view, 'views':OI_PRJ_VIEWS, 'types':SPEC_TYPES, 'table_overview': OI_TABLE_OVERVIEW, 'release': request.session.get("releases", {}).get(project.master.id, "")})

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
                tasks = project.descendants.filter_perm(request.user, OI_READ)
            else:
                request.session.get("release", {})[project.master.id] = ""
                tasks = project.tasks.filter_perm(request.user, OI_READ)
            
            #this function is use to filter on overview tble             
            tasks = filteroverview(request, tasks)
            
            #this function sort on the project for the release
            tasks = releaseoverview(request, tasks, project)
            
            #this function sort by order        
            tasks = orderoverview(request, tasks)
            
            #this function paginate on overview table
            dict_overview = paginateoverview(request, tasks)
            tasks = dict_overview['tasks']
            lists.append({'num_pages':dict_overview['num_pages'] ,'nbtask':dict_overview['nbtask']})
                    
            #appends the serialized task list to the global list
            lists.append(serializers.oiserialize("json", tasks,
                extra_fields=("author.get_profile","assignee.get_profile.get_display_name","get_budget","allbid_sum",
                    "bid_set.count","target.name","target.done","target.project","created","start_date",
                    "due_date","validation", "githubsync_set.get.repository", "githubsync_set.get.label","tasks.count")))
    return HttpResponse(JSONEncoder().encode(lists)) #serializes the whole thing

def paginateoverview(request, tasks):
    """paginate tasks on overview table"""
    paginator = Paginator(tasks, 25, 0, True)
    if request.GET.has_key('page'):
        paginator = Paginator(tasks, 25, 0, True)
        page = request.GET.get('page')
        try:
            tasks = paginator.page(page).object_list
        except PageNotAnInteger:
            tasks = paginator.page(1).object_list
        except EmptyPage:
            tasks = paginator.page(paginator.num_pages).object_list
    return {'num_pages':paginator.num_pages, 'nbtask':tasks.count(), 'tasks':tasks}

def orderoverview(request, tasks):
    """sort with ascending order or decreasing order"""
    if request.GET.has_key("order"):
        tasks = tasks.order_by(request.GET['order'])
    else:
        tasks = tasks.order_by('-priority')
    return tasks

def releaseoverview(request, tasks, project):
    """can sort on the project for the release"""
    if request.GET.get("release"):
        releases = request.session.get("releases", {})
        releases[project.master.id] = request.GET['release']
        request.session["releases"] = releases
        if request.GET['release'] != '**':
            if request.GET['release'] == '*':
                tasks = tasks.filter(Q(target__isnull=True)|Q(descendants__isnull=False, descendants__target__isnull=True)).distinct()
            
            else:
                tasks = tasks.filter(Q(target__name = request.GET['release'])|Q(descendants__target__name = request.GET['release'])).distinct()
    return tasks

def filteroverview(request, tasks):
    """filter on overview table"""
    #this queryset filter with request key 'filter_title' in overview table   
    if request.GET.get('filter_title'):
        tasks = tasks.filter(title__contains=request.GET['filter_title'])
       
    #this queryset filter with request key 'filter_state' in overview table     
    if request.GET.get('filter_state'):
        tasks = tasks.filter(state=request.GET['filter_state'])
     
    #this queryset filter with request key 'filter_echeance' in overview table    
    if request.GET.get('filter_echeance'):
        tasks = tasks.filter(
            Q(start_date__gte=datetime.now(), start_date__lte=datetime.now()+timedelta(0, int(request.GET['filter_echeance'])))|
            Q(due_date__gte=datetime.now(), due_date__lte=datetime.now()+timedelta(hours=0, seconds=int(request.GET['filter_echeance'])))|
            Q(validation__gte=datetime.now(), validation__lte=datetime.now()+timedelta(0, int(request.GET['filter_echeance']))))
    
    #this queryset filter with request key 'filter_assignee' in overview table    
    if request.GET.get('filter_assignee'):
        tasks = tasks.filter(assignee__username=request.GET['filter_assignee'])
        
    if request.GET.get('filter_budget_min') and request.GET.get('filter_budget_max'):
        tasks = tasks.filter(Q(offer__gte=request.GET['filter_budget_min']),Q(offer__lte=request.GET['filter_budget_max']))
      
    #this queryset filter with request key 'filter_release' in overview table  
    if request.GET.get('filter_release'):
        tasks = tasks.filter(target__name__contains=request.GET['filter_release'])
    return tasks

@OINeedsPrjPerms(OI_MANAGE)
def addrelease(request, id):
    """Add a new release to the project"""
    if request.POST["release"] == "" or request.POST["release"] == None:
        return HttpResponse(_("Not empty release"))
    if request.POST["release"] == "Initial release":
        return HttpResponse(_("Release already existing"))
    if request.POST["release"] == "*" or request.POST["release"] == "**":
        return HttpResponse(_("The character '*' is not allowed"))
    Release(name = request.POST["release"], project = Project.objects.get(id=id).master).save()
    return HttpResponse(_("New release added"))

@OINeedsPrjPerms(OI_MANAGE)
def changerelease(request, id):
    """Change the release"""

    #get the master id of the project    
    master = Project.objects.get(id=id).master
    
    release = Release.objects.get(name = request.POST["release"], project=master)
    if release.done == True:
        return HttpResponse(_("Already done"))
        
    if not master.target:
        master.target = Release.objects.create(name = _("Initial release"), project = master)
        
    #make a filter on the descendant master project, and update them
    master.descendants.filter(state__gte = 4, target__isnull=True).update(target=master.target)
    master.descendants.filter(state__lt = 4, target = master.target).update(target=release)

    #make the old release done true
    master.target.done = True
    master.target.due_date = datetime.now()
    master.target.save()
    
    #make the new release become the current release
    master.target = release
    master.save()
    
    master.notify_all(request.user, "change_release", master.target.name)
    
    return HttpResponse(_("Release changed"), status=332)   

@OINeedsPrjPerms(OI_MANAGE)
def assignrelease(request, id):
    project = Project.objects.get(id=id)
    
    release = Release.objects.get(name = request.POST["release"], project = project.master)
    if release.done == True:
        return HttpResponse(_("Can't set to a release already finished"))
    
    if project == project.master:
          return HttpResponse(_("The project master can't be assigned a release"))  
    project.target = release
    
    if project.descendants.filter_perm(request.user, OI_MANAGE):
        for task in project.descendants.filter_perm(request.user, OI_MANAGE):
            task.target = release
            task.save()
    
    project.save() 
    return HttpResponse(_("Release assigned"))

@OINeedsPrjPerms(OI_MANAGE)    
def savereward(request, id, rewardid): 
    """Save Reward""" 
    project = Project.objects.get(id=id)
    
    #new reward
    if rewardid == '0':
        form = RewardForm(request.POST, request.FILES)
        reward = form.save(commit=False)
        reward.project = project
        
    #existing reward
    else:
        form = RewardForm(request.POST, request.FILES, instance=project.reward_set.all().get(id=rewardid))
        reward = form.save(commit=False)
       
    reward.description = oiescape(request.POST["description"]) 
    reward.save()
    return HttpResponse("<script>window.parent.location.reload(true)</script>")

@OINeedsPrjPerms(OI_MANAGE)
def updatestockreward(request, id, rewardid):
    """Add or remove reward"""
    project = Project.objects.get(id=id)
    reward = Reward.objects.get(id=rewardid)
    
    if not project == reward.project:
       return HttpResponse (_("Wrong arguments"))
       
    if request.POST.get("update"):
        reward.nb_reward = reward.nb_reward + int(request.POST.get("update"))
        if reward.nb_reward > 0:
            reward.show = True
        
    if reward.nb_reward < 0:
        reward.show = False
        
    if reward.show == False:
        return HttpResponse (_("No more reward"))
    
    reward.save()
    return HttpResponse (_("The stock has been changed"))
    
  
@OINeedsPrjPerms(OI_MANAGE)
def deletereward(request, id, rewardid):
    """Delete the reward"""
    project = Project.objects.get(id=id)
    reward = Reward.objects.get(id=rewardid)
    
    if not project == reward.project:
       return HttpResponse (_("Wrong arguments"))
       
    reward.delete()
    return HttpResponse(_("Reward deleted"))
    
@login_required
def editproject(request, id):
    """Shows the Edit template of the project"""
    project=None
    if id!='0':
        project = Project.objects.get(id=id)
        if not project.has_perm(request.user, OI_WRITE):
            return HttpResponseForbidden(_("Forbidden"))
    return direct_to_template(request, template='projects/editproject.html', extra_context={'user': request.user, 'parent':request.GET.get("parent"), 'project':project})

def create_new_task(parent, title, author, githubid=None):
    if parent:
        parent.inc_tasks_priority(0)
    project = Project(title=title, author=author, parent=parent, githubid=githubid)
    project.save()
    # permission handling
    project.set_perm(author, OI_ALL_PERMS)
    project.inherit_perms()
    # assigns task
    assignee = parent.assignee if parent else author
    if assignee:
        project.assign_to(assignee)
    # github sync
    if parent and parent.githubsync_set.all() and not githubid:
        repo = parent.get_repo()
        if repo:
            if parent.githubsync_set.get().label:
                labels = [repo.get_label(parent.githubsync_set.get().label)]
            else:
                labels = []
            project.githubid = repo.create_issue(project.title, body="http://www.openinitiative.com/project/%s/view/description/"%project.id, labels=labels).id
        project.save()
    return project

@ajax_login_required(keep_fields=('title','app'))
def saveproject(request, id='0'):
    """Saves the edited project and redirects to it"""
    parent = Project.objects.get(id=request.POST["parent"]) if request.POST.get("parent") else None
    if (parent and parent.state > 3):
        return HttpResponse(_("Can not change a finished task"), status=431)

    title = request.POST.get("title") or request.session.get('title')
    if not title:
        return HttpResponse(_("Please enter a title"), status=531)
    
    if request.POST.get("offer") and not request.POST["offer"].isdigit():
        return HttpResponse(_("Please enter a digital value"), status=431)    
    
    if id=='0': #new project
        project = create_new_task(parent, title, request.user)
        
        target_name = request.session.get("releases", {}).get(project.master.id, "")
        if target_name:
            if target_name != "*" and target_name != "**":
                get_release = Release.objects.get(name = target_name, project = project.master)
                if get_release.done == False:
                    project.target = get_release
    else: #existing project
        project = Project.objects.get(id=id)
        if not project.has_perm(request.user, OI_ANSWER):
            return HttpResponseForbidden(_("Forbidden"))
        project.title = request.POST["title"]

    for field in ["start_date","due_date","validaton","progress", "offer"]:
        if request.POST.has_key(field) and len(request.POST[field])>0:
            project.__setattr__(field, request.POST[field])
            if field == "offer":
                project.commission = Decimal("0"+request.POST[field]) * OI_COMMISSION
                
    project.state = OI_PROPOSED
    project.check_dates()
    project.save()

    #notify users about this project
    project.notify_all(request.user, "new_project", "")
    #adds the project to user's observation
    request.user.get_profile().follow_project(project.parent or project)
    if request.POST.get("inline","0") == "1":
        return HttpResponse(serializers.serialize("json", [project]))
    else:
        return HttpResponseRedirect('/%s/%s'%(request.session.get("app", "project"), project.id))

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

@OINeedsPrjPerms(OI_MANAGE)
def sorttasks(request, id):
    """Sorts tasks in a project by setting priority to each of it"""
    project = Project.objects.get(id=id)
    if project.parent:
        return HttpResponse(_("Cannot sort tasks inside a task"), status=431)
    if project.state > OI_DELIVERED:
        return HttpResponse(_("Can not change a finished project"), status=431)
        
    for param,value in request.POST.items():
        if param.startswith("task_"):
            Project.objects.filter(id=param[5:]).update(priority=value)
    return HttpResponse(_("Features sorted"))

@OINeedsPrjPerms(OI_WRITE)
def edittitle(request, id):
    """Changes the title of the project"""
    project = Project.objects.get(id=id)
    
    if project.state > OI_STARTED:
        return HttpResponse(_("Can not change a finished task"), status=431)
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
    project.set_perm(project.assignee, OI_WRITE)
    project.descendants.apply_perm(project.assignee, OI_WRITE)
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
        project.assign_to(request.user, requester=project.assignee)
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

@ajax_login_required
@OINeedsPrjPerms(OI_BID)
def bidproject(request, id):
    """Makes a new bid on the project"""
    project = Project.objects.get(id=id)
    try:
        amount = Decimal("0"+request.POST.get("bid","0").replace(",","."))
    except InvalidOperation:
        return HttpResponse(_("Invalid amount"))
    #checks that the user can afford the bid ; if not, redirects to the deposit page
    
    #1) check amount
    if amount == 0:
        return HttpResponse(_('Please indicate the amount'))
    
    #2) calcul the missing
    missing = amount - request.user.get_profile().balance
    if amount > request.user.get_profile().balance:
        amount = request.user.get_profile().balance
    
   #3) check if the project progress is 100% funded
    if project.allbid_sum() < project.offer + project.commission + project.get_commission_tax() and project.allbid_sum() + amount >= project.offer + project.commission + project.get_commission_tax():
        #4) notify users about the progress
        project.notify_all(project.assignee, "project_progress_users", project.progress)
        #5) notify developper about the progress
        project.assignee.get_profile().get_default_observer(project).notify("project_progress_dev", project=project)

    #5) make the bid with the amount
    project.makebid(request.user, amount) #to update the user account

    #6) back to ogone if is not enough
    if missing > 0:
        return HttpResponse('/user/myaccount?amount=%s&project=%s'%((missing).to_eng_string(),project.id),status=333)

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
    
    for task in project.descendants.filter_perm(user, OI_READ):
        bid, created = Bid.objects.get_or_create(project=task, user=user)
    
    project.set_perm(user, OI_BID)
    project.descendants.apply_perm(user, OI_BID)
    user.get_profile().follow_project(project.master)
    user.get_profile().get_default_observer(project).notify("validate_project", project=project, sender=request.user)
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
    if project.bid_sum() != 0:
        return HttpResponse(_("Can not delete a started project. Please stop it first and cancel your bid."))
    if project.tasks.count() > 0:
        return HttpResponse(_("Can not delete a project containing tasks. Please delete all its tasks first."))
    
    project.notify_all(request.user, "project_delete", project.title)
    project.notice_set.filter(project=project).update(project=None)
    project.delete()
    return HttpResponse(_("The task %s has been deleted.")%(project.title))

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
    #remove dependencies between ancestors and descendants
    for task in project.descendants.filter(Q(requirements=parent)|Q(requirements__descendants=parent)):
        task.requirements.remove(task.requirement.filter(Q(id=parent.id)|Q(descendants=parent)))
    for task in project.descendants.filter(Q(dependants=parent)|Q(dependants__descendants=parent)):
        task.dependants.remove(task.dependants.filter(Q(id=parent.id)|Q(descendants=parent)))
    project.parent = parent
    parent.inc_tasks_priority(priority)
    project.priority = priority
    project.save()
    for task in project.descendants.all():
        task.save() #recompute ancestors
    return HttpResponse(_("Task moved"))

@OINeedsPrjPerms(OI_MANAGE)
def addrequirement(request, id):
    """Adds a dependency to the project"""
    project = Project.objects.get(id=id)
    if not request.POST.get("req"):
        return HttpResponse(_("Wrong arguments"), status=531)
    requirement = Project.objects.get(id=request.POST["req"])
    if project==requirement or project.descendants.filter(id=requirement.id) or project.ancestors.filter(id=requirement.id):
        return HttpResponseForbidden(_("Can not create a dependency with an ancestor or a descendant"))
    project.requirements.add(requirement)
    project.check_dates()
    return HttpResponse(u"%s : %s €"%(requirement.title, requirement.missing_bid()))

@OINeedsPrjPerms(OI_MANAGE)
def removerequirement(request, id):
    """Removes a dependency to the project"""
    project = Project.objects.get(id=id)
    if not request.POST.get("req") or not project.requirements.filter(id=request.POST["req"]):
        return HttpResponse(_("Wrong arguments"), status=531)
    project.requirements.remove(request.POST["req"])
    return HttpResponse("Dependency removed")

@OINeedsPrjPerms(OI_MANAGE)
def setpublicproject(request, id):
    """Makes the project private or public and outputs a message"""
    project = Project.objects.get(id=id)
    for permission in ['read', 'answer', 'bid']:
        if request.POST.get(permission):
            project.__setattr__("public_"+permission, request.POST[permission]=="true")
            project.save()
            project.descendants.apply_public(permission, request.POST[permission]=="true")
    return HttpResponse(_("Permissions set"))

@OINeedsPrjPerms(OI_MANAGE)
def shareproject(request, id):
    """Shares the project with a user and outputs a message"""
    project = Project.objects.get(id=id)
    try:
        user = User.objects.get(username=request.POST["username"])
    except (KeyError, User.DoesNotExist):
        return HttpResponse(_("Cannot find user"), status=531)
    project.set_perm(user, OI_BID)
    project.descendants.apply_perm(user, OI_BID)
    project.set_perm(user, OI_READ)
    project.descendants.apply_perm(user, OI_READ)
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
def setgithubsync(request, id):
    """sets a GitHub synchronization on that project"""
    project = Project.objects.get(id=id)
    try:
        githubsync = GitHubSync.objects.get(project = project)
    except GitHubSync.DoesNotExist:
        githubsync = GitHubSync(project = project)
    githubsync.githubowner = request.POST['github_login']
    githubsync.repository = request.POST['github_repo']
    githubsync.label = request.POST['label']
    githubsync.save()
    return HttpResponse(_('Settings saved'))
    
@OINeedsPrjPerms(OI_MANAGE)
def setgihubtoken(request, id):
    """Sets a token on a github synchronization for authorization"""
    project = Project.objects.get(id=id)
    if not int(request.GET['state']) == request.user.id:
        messages.info(request, _("Forbidden: could not identify requester"))
        return HttpResponseRedirect("/project/%s/view/github"%project.id)
    params = urlencode({'client_id': github_id, 'client_secret': github_secret, 'code': request.GET['code'], 'state': request.GET['state']})
    req = Request('https://github.com/login/oauth/access_token', params, {'Accept': 'application/json'})
    response = JSONDecoder().decode(urlopen(req).read())
    if response.has_key('error'):
        messages.info(request, _("Github error: %s")%response["error"])
    else:
        githubsync, created = GitHubSync.objects.get_or_create(project = project)
        githubsync.token = response["access_token"]
        githubsync.save()
        messages.info(request, _("Project authorized"))
    return HttpResponseRedirect("/project/%s/view/github"%project.id)
    
@OINeedsPrjPerms(OI_MANAGE)
def getgithubrepos(request, id):
    """list all repository available with given token"""
    project = Project.objects.get(id=id)
    repos = project.githubsync_set.get().list_repos()
    repos = dict(map(lambda (login,repo_list): (login, [repo.name for repo in repo_list]), repos.items()))
    return HttpResponse("(%s)"%JSONEncoder().encode(repos))
    
@OINeedsPrjPerms(OI_MANAGE)
def syncgithub(request, id):
    """Synchronises the tasks with the github issues"""
    project = Project.objects.get(id=id)
    repo = project.get_repo()
    for issue in repo.get_issues(): # all issues in repository
        if not Project.objects.filter(githubid=issue.number): 
            if project.githubsync_set.get().accept_issue_label(issue):
                task = create_new_task(project, issue.title, request.user, issue.number)
                Spec.objects.create(project=task, type=1, text=issue.body, url=issue.url, order=project.get_max_order()+1)
    return HttpResponse('', status=332)
    
@OINeedsPrjPerms(OI_MANAGE)
def togglegithubhook(request, id):
    """Set a Github hook on the current project, to create a task each time an issue is created
    or deletes it if it exists"""
    project = Project.objects.get(id=id)
    hook = project.get_hook()
    if hook:
        hook.delete()
        return HttpResponse(_("Hook deleted"))
        
    url = "%s/project/%s/createtask"%(get_current_site(request).domain, id)
    project.get_repo().create_hook("web", {'url': url}, ["issues", "issue_comments"])
    return HttpResponse(_("Hook created"))

@csrf_exempt
def createtask(request, id):
    """Create task on GitHub hook"""
    import logging, sys
    project = Project.objects.get(id=id)
    try:
        data = JSONDecoder().decode(request.POST["payload"])
        logging.getLogger("oi").debug("Github: "+data.get("action"))
        #Check if one of the issue's labels is synchronised in a project
        for label in data["issue"].get("labels", [{"name": None}]):
            for githubsync in GitHubSync.objects.filter(repository=data["repository"]["name"], label=label["name"]):
                if project == githubsync.project:
                    if data.get("action") == "opened":
                        create_new_task(project, data["issue"].get("title"), githubsync.user, data["issue"].get("number"))
                        Spec.objects.create(project=project, type=1, text=issue.body, url=issue.url, order=project.get_max_order()+1)
        return HttpResponse('OK')
    except Exception:
        logging.getLogger("oi").debug("Github Sync Error : " + sys.exc_info())
        return HttpResponse('', status=422)
    
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
    type = int(request.GET["type"])
    project = Project.objects.get(id=id)
    spec=None
    if specid!='0':
        if project.state > OI_ACCEPTED:
            return HttpResponse(_("Can not change a task already started"), status=431)
        spec = Spec.objects.get(id=specid)
        if spec.project.id != int(id):
            return HttpResponse(_("Wrong arguments"), status=531)
    return direct_to_template(request, template='projects/spec/edit_type%s.html'%(type), extra_context={'user': request.user, 'divid': request.GET["divid"], 'project':project, 'spec':spec})

@login_required
@OINeedsPrjPerms(OI_WRITE)
def savespec(request, id, specid='0'):
    """saves the spec"""
    project = Project.objects.get(id=id)
    
    if specid=='0': #new spec
        order = int(request.POST.get("order", -1))
        if order==-1:
            order = project.get_max_order()+1
        else:
            if project.state > OI_STARTED:
                return HttpResponse(_("Can not change a task already started"), status=431)
            #project.insert_spec(order) #specs with different languages can now have order

        spec = Spec(text = oiescape(request.POST["text"]), author=request.user, project=project, order=order, type=1, language = request.POST.get("language"))

    else: #edit existing spec
        spec = Spec.objects.get(id=specid)
        if spec.project.id != int(id): #checks project id
            return HttpResponse(_("Wrong arguments"), status=531)
        spec.text = request.POST.get("legend") or oiescape(request.POST["text"])
        if request.POST.get("language"): 
            spec.language = request.POST.get("language")
            
    if request.POST.has_key("url"):
        spec.url = request.POST["url"]
    if request.POST.has_key("type"):
        spec.type = int(request.POST["type"])
    
    filename = request.POST.get("filename")
    
    if not filename and not spec.file and spec.type in (2,5):
        return HttpResponse(_("Wrong arguments"), status=531)
    if filename:
#        filename = normalize("NFC", filename) #this encoding should work with next version of xsendfile
        filename = normalize("NFKD", filename).encode('ascii', 'ignore').replace('"', '')
        if spec.file:
            spec.file.delete()
        path = ("%s%s_%s_%s"%(TEMP_DIR,request.user.id,request.POST["ts"],filename))
        spec.file.save(filename, File(open(path)), False)
        os.remove(path)
        
    spec.save()

    #notify users about this spec change
    project.notify_all(request.user, "project_spec", spec.text)
    #I waiting for the best solution
    redirect_url = settings.REDIRECT_URL
    if redirect_url == "/project/":
        redirect_url = "/projects/"
    return render_to_response('%sspec/spec.html'%(redirect_url[1:]),{'user': request.user, 'project' : project, 'spec' : spec})
    

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
    if spotid=="0": #new spot
        spot = Spot(spec = Spec.objects.get(id=specid))
        if spot.spec.project.id != int(id):
            return HttpResponse(_("Wrong arguments"), status=531)
    else:
        spot = Spot.objects.get(id=spotid)
        if spot.spec.project.id != int(id) or spot.spec.id != int(specid):
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
    #I waiting for the best solution 
    redirect_url = settings.REDIRECT_URL
    if redirect_url == "/project/":
        redirect_url = "/projects/"
    return render_to_response('%sspec/fileframe.html'%(redirect_url[1:]),{'divid':divid,'filename':filename,'ts':ts,'projectid':id})

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
        desc = _("Created by") + " " + item.author.get_profile().get_display_name()
        for spec in item.spec_set.all():
            desc += "\n- " + summarize(spec.text)
        return desc
        
    def item_link(self, item):
        return "/project/%s"%item.id
