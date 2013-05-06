# coding: utf-8
# Modèles des projets
from datetime import datetime, timedelta
from decimal import Decimal
from github import Github, GithubException
from re import match
from django.db import models
from django.db.transaction import commit_on_success
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.db.models.query import QuerySet
from oi.settings import MEDIA_ROOT
from oi.helpers import OI_ALL_PERMS, OI_PERMS, OI_RIGHTS, OI_READ, OI_WRITE, OI_ANSWER, OI_BID, OI_MANAGE, OI_COMMISSION, OI_COM_ON_BID, OI_CANCELLED_BID, OI_VAT_RATE
from oi.helpers import OI_PRJ_STATES, OI_PROPOSED, OI_ACCEPTED, OI_STARTED, OI_DELIVERED, OI_VALIDATED, OI_CANCELLED, OI_POSTPONED, OI_CONTENTIOUS, OI_TABLE_OVERVIEW
from oi.helpers import SPEC_TYPES, TEXT_TYPE, to_date
from oi.prjnotify.models import Observer

class ProjectQuerySet(QuerySet):
    def with_offer(self):
        """includes only projects with an offer"""
        return self.filter(offer__gt = 0)
    
    def filter_perm(self, user, permission):
        """filter projects on permissions"""
        if user.is_superuser: #Super user has all permissions on all tasks
            return self.all()
        if permission==OI_READ:
            return self.filter(models.Q(public_read=True)|models.Q(projectacl__user=user if user.is_authenticated() else None, projectacl__permission=permission)).distinct()
        elif permission==OI_ANSWER:
            return self.filter(models.Q(public_answer=True)|models.Q(projectacl__user=user if user.is_authenticated() else None, projectacl__permission=permission)).distinct()
        if permission==OI_BID:
            return self.filter(models.Q(public_bid=True)|models.Q(projectacl__user=user if user.is_authenticated() else None, projectacl__permission=permission)).distinct()
        else:
            return self.filter(projectacl__user=user if user.is_authenticated() else None, projectacl__permission=permission).distinct()
            
    def apply_perm(self, user, perm):
        """sets perm on all projects in queryset"""
        for task in self:
            task.set_perm(user, perm)

    def apply_public(self, permission, public):
        """sets public on all projects in queryset"""
        return self.update(**{"public_"+permission: public})

#Add function for the list
class ProjectManager(models.Manager):
    def get_query_set(self):
        """Returns a new QuerySet object.  Subclasses can override this method
        to easily customize the behavior of the Manager.
        """
        return ProjectQuerySet(self.model, using=self._db)
        
    def filter_perm(self, *args, **kwargs):
        return self.get_query_set().filter_perm(*args, **kwargs)
            
    def with_offer(self, *args, **kwargs):
        return self.get_query_set().with_offer(*args, **kwargs)
        
    def apply_perm(self, *args, **kwargs):
        return self.get_query_set().apply_perm(*args, **kwargs)
        
    def apply_public(self, *args, **kwargs):
        return self.get_query_set().apply_public(*args, **kwargs)
        
# A project can contain subprojects and/or specs. Without them it is only a task
class Project(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, related_name='ownprojects', null=True, blank=True)
    assignee = models.ForeignKey(User, related_name='assigned_projects', null=True, blank=True)
    delegate_to = models.ForeignKey(User, related_name='delegated_projects', null=True, blank=True)
    offer = models.DecimalField(max_digits= 12, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits= 12, decimal_places=2, default=0)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='tasks')
    ancestors = models.ManyToManyField('self', symmetrical=False, related_name='descendants', blank=True)
    master = models.ForeignKey('self', blank=True, null=True, related_name='subprojects')
    requirements = models.ManyToManyField('self', symmetrical=False, related_name='dependants', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    validation = models.DateTimeField(blank=True, null=True)
    delay = models.DateTimeField(blank=True, null=True)
    progress = models.IntegerField(default=0.0)
    priority = models.IntegerField(default=0)
    state = models.IntegerField(choices=OI_PRJ_STATES, default=OI_PROPOSED)
    public = models.BooleanField(default=True)
    public_read = models.BooleanField(default=True)
    public_answer = models.BooleanField(default=False)
    public_bid = models.BooleanField(default=False)
    target = models.ForeignKey("projects.Release", null=True, blank=True, related_name="tasks")
    githubid = models.IntegerField(blank=True, null=True)
    objects = ProjectManager()
    
    # overloads save to compute master project and ancestors
    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
        ancestors = []
        parent = self
        while parent.parent:
            parent = parent.parent
            ancestors += [parent]
        self.master = parent
        self.ancestors = ancestors
        super(Project, self).save(*args, **kwargs)
    
    def check_dates(self):
        """Fixes incorrect dates : the dates should be in the right order"""
        if self.start_date:
            if to_date(self.created) > to_date(self.start_date):
                self.start_date = self.created
            for req in self.requirements.all(): #checks that the project doesn't start before the requirement is due
                if req.due_date and to_date(req.due_date) > to_date(self.start_date):
                    self.start_date = req.due_date
            if self.due_date:
                if to_date(self.start_date) > to_date(self.due_date):
                    self.due_date = self.start_date
                if self.validation and to_date(self.due_date) > to_date(self.validation):
                    self.validation = to_date(self.due_date)
        for dep in self.dependants.all(): #checks if dependants are impacted by date modications
            dep.check_dates()
    
    def update_tree(self):
        """checks if ancestors and descendants states and dates are consistent with the task"""
        if self.state == OI_STARTED:
            for ancestor in self.ancestors.filter(state__lt = OI_STARTED):
                #start all ancestors not yet started if task is started
                if not ancestor.switch_to(OI_STARTED, None):
                    return False
        if self.state == OI_DELIVERED:
            for descendant in self.descendants.filter(state__lt = OI_DELIVERED):
                #update all descendants not yet delivered if project is delivered
                if not descendant.switch_to(OI_DELIVERED, None):
                    return False
        if self.state == OI_VALIDATED:
            for descendant in self.descendants.filter(state__lt = OI_VALIDATED):
                #update all descendants not yet delivered if project is delivered
                if not descendant.switch_to(OI_VALIDATED, None):
                    return False
    
        if self.start_date:
            for ancestor in self.ancestors.filter(start_date__gt = self.start_date):
                #ancestor start date should be before task start date
                ancestor.start_date = self.start_date
                ancestor.check_dates()
                ancestor.save()
        if self.due_date:
            for ancestor in self.ancestors.filter(due_date__lt = self.due_date):
                #ancestor due date should be after task due date
                ancestor.due_date = self.due_date
                ancestor.check_dates()
                ancestor.save()

        if self.start_date:
            for descendant in self.descendants.filter(start_date__lt = self.start_date):
                #descendant start date should be after project start date
                descendant.start_date = self.start_date
                descendant.check_dates()
                descendant.save()
        if self.due_date:
            for descendant in self.descendants.filter(due_date__gt = self.due_date):
                #descendant due date should be before project due date
                descendant.due_date = self.due_date
                descendant.check_dates()
                descendant.save()
        return True
    
    def switch_to(self, newstate, user):
        """Changes the state of the project, if allowed, and """
        if user:
            #check state
            if self.state+1 != newstate: 
                if not (self.state==newstate==OI_ACCEPTED): #accepts same state if it is OI_ACCEPTED
                    if not (newstate==OI_STARTED and self.state==OI_PROPOSED): #accepts to switch from proposed to started
                        return False
            
            #check user
            if not (self.is_bidder(user)): #only bidders can switch to validated
                if newstate == OI_VALIDATED:
                    return False
            if not (user == self.assignee): #only the assignee can switch to started or delivered
                if newstate == OI_STARTED or newstate == OI_DELIVERED:
                    return False
            if not (self.is_bidder(user)) and not (user == self.assignee): #other users can not change state
                return False
    
        #update state
        if newstate < OI_STARTED: #before start, project is accepted iff bids complete the offer
            newstate = OI_ACCEPTED if self.is_ready_to_start() else OI_PROPOSED
        elif newstate >= OI_DELIVERED: #validate the project iff all bidders validated
            newstate = OI_VALIDATED if self.bid_set.filter(validated=False).count()==0 else OI_DELIVERED
            
        if self.state != newstate: #state needs to be updated
        
            #update dates
            if self.state < OI_STARTED and newstate == OI_STARTED:
                self.start_date = datetime.now()
            if self.state == OI_STARTED and newstate > OI_STARTED:
                self.due_date = datetime.now()
            if self.state < OI_VALIDATED and newstate == OI_VALIDATED:
                self.validation = datetime.now()
            self.check_dates()
            self.state = newstate
            
            #update tree states
            if user:
                if not self.update_tree():
                    return False
            self.save()
            #notify users of state change
            if user:
                self.notify_all(user, "project_state", OI_PRJ_STATES[self.state][0])
        return True

    @commit_on_success
    def inc_tasks_priority(self, priority):
        """increases the priority of all tasks to insert a less prioritary one"""
        for task in self.tasks.filter(priority__gte=priority):
            task.priority = task.priority+1
            task.save()

    def get_max_order(self):
        """Returns the position of the last spec of the project"""
        return self.spec_set.aggregate(maxorder=models.Max('order'))['maxorder'] or 0
        
    def insert_spec(self, order):
        """insert a spec at the given position"""
        for spec in self.spec_set.filter(order__gte=order):
            spec.order += 1
            spec.save()
            
    def is_simple_task(self):
        """A simple task is a project with no subproject"""
        return self.tasks.count() == 0
    
    def is_late(self):
        """A task is late when its due date is passed but it is not completely done"""
        return self.progress < 100 and self.due_date < datetime.now()
    
    def has_perm(self, user, perm):
        """checks if the user has the required perms"""
        #superuser always has all permissions
        if user.is_superuser:
            return True
        if perm == OI_READ and self.public_read:
            return True
        if perm == OI_ANSWER and self.public_answer:
            return True
        if perm == OI_BID and self.public_bid:
            return True
        if user.is_anonymous():
            return False
        return len(self.projectacl_set.filter(user=user,permission=perm))>0
    
    def set_perm(self, user, perm):
        """adds the specified perm to the user"""
        if user.is_authenticated:
            if perm == OI_ALL_PERMS:
                for right in OI_RIGHTS:
                    self.projectacl_set.get_or_create(user=user, permission=right)
            else:
                self.projectacl_set.get_or_create(user=user, permission=perm)
    
    @commit_on_success
    def inherit_perms(self):
        """gets all perms from parent and sets them to the project"""
        if self.parent:
            self.public_read = self.parent.public_read
            self.public_answer = self.parent.public_answer
            self.public_bid = self.parent.public_bid
            self.save()
            for perm in self.parent.projectacl_set.all():
                self.set_perm(perm.user, perm.permission)
            
    @commit_on_success
    def assign_to(self, user, requester=None):
        """sets project and descendants' assignee"""
        if user.is_authenticated:
            if requester:
                if self.has_perm(requester, OI_MANAGE):
                    self.assignee = user
                    self.save()
                    self.set_perm(user, OI_MANAGE)
                    tasks = self.descendants.filter_perm(requester, OI_MANAGE)
                    tasks.update(assignee=user)
                    tasks.apply_perm(user, OI_MANAGE)
                    self.set_perm(requester, OI_BID)
                    tasks.apply_perm(requester, OI_BID)
                    bid, created = Bid.objects.get_or_create(project=self, user=requester)
                    for task in tasks:
                        bid, created = Bid.objects.get_or_create(project=task, user=requester)
            else:
                self.assignee = user
                self.save()
                self.descendants.update(assignee=user)
                self.set_perm(user, OI_MANAGE)
                self.descendants.apply_perm(user, OI_MANAGE)
            if self.githubid and self.assignee and self.assignee.get_profile().github_username:
                repo = self.parent.get_repo()
                github_user = self.parent.get_gituser(self.assignee.get_profile().github_username)
                issue = repo.get_issue(self.githubid)
                issue.edit(assignee=github_user)

    def notify_all(self, sender, notice_type, param):
        """sends a notification to all users about this project"""
        for observer in Observer.objects.filter(models.Q(project=self)|
                models.Q(project__descendants=self)).exclude(user=sender).distinct():
            observer.notify(label=notice_type, project=self, param=param, sender=sender)

    def canceled_bids(self):
        """gets all the bids marked as canceled"""
        return self.bid_set.filter(rating=OI_CANCELLED_BID)
    
    def is_bidder(self, user):
        return user.is_authenticated() and self.bid_set.filter(user=user).filter(rating=None).count() > 0

    def allbid_sum(self):
        """sums up all bids on the project's tasks"""
        return (self.descendants.aggregate(models.Sum("bid__amount"))["bid__amount__sum"] or Decimal("0")) + self.bid_sum()
        
    def alloffer_sum(self):
        """sums up all offers on the project's tasks"""
        return self.descendants.aggregate(models.Sum("offer"))["offer__sum"] or Decimal("0")
    
    def allcommission_sum(self):
        """sums up all commissions on the project's tasks"""
        return self.descendants.aggregate(models.Sum("commission"))["commission__sum"] or Decimal("0")
    
    def get_offer_tax(self):
        """sums up all commissions on the project's tasks"""
        if self.assignee:
            return (self.offer or self.alloffer_sum()) * (self.assignee.get_profile().tax_rate or 0) / 100
        else:
            return 0
    
    def get_commission_tax(self):
        """sums up all commissions on the project's tasks"""
        return (self.commission or self.allcommission_sum()) * OI_VAT_RATE / 100
        
    def get_budget(self):
        """return the total budget of the project, either itself or summing its tasks, and including commission"""
        return (self.offer or self.alloffer_sum()) + self.get_offer_tax() + (self.commission or self.allcommission_sum()) + self.get_commission_tax()
    
    def get_funding_progress(self):
        """Returns the percentage of offer already in bids"""
        if self.get_budget():
            return min(self.allbid_sum() / self.get_budget() * 100, 100)
        else:
            return None
    
    def bid_sum(self):
        """returns the sum of all bids on this project"""
        return self.bid_set.aggregate(models.Sum("amount"))["amount__sum"] or 0
    
    def missing_bid(self):
        """returns how much the project still needs to be started"""
        return max(self.get_budget() - self.bid_sum(), Decimal("0")) + self.missing_requirement_bid()
    
    def missing_requirement_bid(self):
        """returns the total amount missing on all requirements"""
        return sum(map(lambda r: r.missing_bid(), self.requirements.all()))
    
    def list_guests(self):
        """returns the list of all users who have permissions on the project but are neither bidders nor assignee"""
        return User.objects.filter(projectacl__project=self).exclude(assigned_projects=self).exclude(bid_projects__project=self).distinct()
    
    def finished_tasks(self):
        """gets all the tasks which state is at least delivered"""
        return self.tasks.filter(state__gte = OI_DELIVERED)
    
    def offered_descendants(self):
        """gets all the descendants which received an offer"""
        return self.descendants.filter(models.Q(offer__gt=0)|models.Q(descendants__offer__gt=0)).distinct()

    def get_path(self):
        """get the location of the task inside the project"""
        if self.parent:
            return self.parent.get_path() + [self]
        else:
            return [self]

    def is_ready_to_start(self):
        """returns True iff the project has enough bids"""
        missing_bid = self.missing_bid()
        return (missing_bid.is_signed() or missing_bid.is_zero())
    
    def reset_delay_request(self):
        """Remove the delay and resets user ratings"""    
        for bid in self.bid_set.all(): #reset all 
            bid.rating = None
            bid.save()
        self.delay = None
        self.save()
    
    def get_repo(self):
        """gets the github repo attached with the project"""
        try:
            githubsync = self.githubsync_set.get()
            return Github(githubsync.token, user_agent="Open-Initiative/0.1").get_user().get_repo(githubsync.repository)
        except GithubException:
            return None
    
    def get_gituser(self, username):
        """gets the github repo attached with the project"""
        githubsync = self.githubsync_set.get()
        return Github(githubsync.token, user_agent="Open-Initiative/0.1").get_user(username)
    
    def get_hook(self):
        """determines if a project has a hook to Github"""
        repo = self.get_repo()
        if repo:
            for hook in repo.get_hooks():
                if hook.config.get("url"):
                    if match( ".*open.*initiative.*/project/%s/createtask"%self.id, hook.config['url']):
                        return hook
        return None
    
    def __unicode__(self):
        return "%s : %s"%(self.id, self.title)

    def old_releases(self):
        """Show all the old releases"""
        return self.master.release_set.filter(done = True)
        
    def future_releases(self):
        """Show all the releases that are not done yet"""
        return self.master.release_set.filter(done = False).exclude(tasks=self.master)
        
    def all_descendants_assignees(self):
        return User.objects.filter(assigned_projects__ancestors=self).distinct()
        
    #descendanding task for funding    
    def all_started_tasks(self):
        return self.descendants.select_related('author', 'assignee', 'delegate_to', 'parent', 'master', 'target').filter(state = 0)
        
    def all_progress_tasks(self):
        return self.descendants.select_related('author', 'assignee', 'delegate_to', 'parent', 'master', 'target').filter(state__lte=3).exclude(state = 0)
        
    def all_finish_tasks(self):
        return self.descendants.select_related('author', 'assignee', 'delegate_to', 'parent', 'master', 'target').filter(state = 4)
        
#Structure de contrôle des permissions
class ProjectACL(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    permission = models.IntegerField(choices=OI_PERMS)
    class Meta:
        unique_together = (("project", "user", "permission"),)
    def __unicode__(self):
        return "%s on %s: %s"%(self.user, self.project.title, self.permission)

#Décorateur de vérification de permissions
def OINeedsPrjPerms(perm, isajax=True):
    def decorate(f):
        def new_f(request, id, *args, **kwargs):
            #Vérification de toutes les permissions
            prj = get_object_or_404(Project,id=id)
            if not prj.has_perm(request.user, perm):
                if isajax:
                    return HttpResponseForbidden(_("Forbidden"))
                else:
                    raise Http404
            return f(request, id, *args, **kwargs)
        return new_f
    return decorate 

def getpath(instance, filename):
    return "project/%s/%s"%(instance.project.id,filename)

# A spec is the content of a project
class Spec(models.Model):
    author = models.ForeignKey(User, null=True, blank=True)
    project = models.ForeignKey(Project)
    type = models.IntegerField(choices=SPEC_TYPES.items(), default=TEXT_TYPE)
    text = models.TextField(blank=True)
    url = models.URLField(null=True, blank=True)
    file = models.FileField(upload_to=getpath,null=True, blank=True)
    image = models.ImageField(upload_to=getpath,null=True, blank=True)
    order = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    #saves project as well
    def save(self, *args, **kwargs):
        self.project.save()
        super(Spec, self).save(*args, **kwargs)

class Spot(models.Model):
    author = models.ForeignKey(User, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    spec = models.ForeignKey(Spec)
    offsetX = models.IntegerField(default=0)
    offsetY = models.IntegerField(default=0)
    task = models.ForeignKey(Project, null=True, blank=True)
    number = models.IntegerField()
    
    def save(self, *args, **kwargs):
        """puts last number for spec if none is provided"""
        if not self.number:
            self.number = (self.spec.spot_set.aggregate(maxnumber=models.Max('number'))['maxnumber'] or 0) + 1
        super(Spot, self).save(*args, **kwargs)

    def isbug(self):
        """check if the spot contains a bug report"""
        return self.task.spec_set.filter(type=6).count() > 0
            

    def delete(self):
        """renumbers other spots of same spec when a spot is deleted"""
        spec = self.spec
        super(Spot, self).delete()
        for i, spot in enumerate(spec.spot_set.order_by("number")):
            spot.number=i+1
            spot.save()

# Offer of users on projets
class Bid(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User, related_name='bid_projects')
    amount = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    commission = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    validated = models.BooleanField(default=False)
    rating = models.IntegerField(null=True,blank=True)
    comment = models.TextField(blank=True)

    def cancel(self):
        """Cancels the bid : reimburses the bidder, reduces project offer, and deletes the bid"""
        amount = self.amount - self.commission #don't reimburse the commission part of the bid
        self.project.offer -= amount
        self.project.commission -= self.commission
        self.project.save()
        self.user.get_profile().make_payment(amount, _("Refund of bid"), self.project)
        self.delete()

    class Meta:
        unique_together = (("project", "user"),)
    def __unicode__(self):
        return "%s on %s: %s"%(self.user, self.project.title, self.amount)

# Projects promoted on main page
class PromotedProject(models.Model):
    project = models.ForeignKey(Project)
    location = models.CharField(max_length=50)
    def __unicode__(self):
        return "%s(%s)"%(self.project.title, self.location)
        
class Release(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=50)
    due_date = models.DateTimeField(blank=True, null=True)
    done = models.BooleanField()
    
    class Meta:
        unique_together = ("project", "name")
        
    def __unicode__(self):
        return "'%s', on project: '%s', done is: '%s'"%(self.name, self.project.title, self.done)

# GitHub integration
class GitHubSync(models.Model):
    project = models.ForeignKey(Project, unique=True)
    githubowner = models.CharField(max_length=100, blank=True, null=True)
    token = models.CharField(max_length=100, blank=True, null=True)
    repository = models.CharField(max_length=100)
    label = models.CharField(max_length=100, default="")
    
    def list_repos(self):
        """lists all repos an authorized user can use"""
        user = Github(self.token).get_user()
        repos= {user.login: user.get_repos()}
        for org in user.get_orgs():
            repos[org.login] = org.get_repos()
        return repos
    
    def accept_issue_label(self, issue):
        """tests if the issue should be synchronized regarding its labels"""
        if not self.label: # if no label selected, all are accepted
            return True
        for label in issue.get_labels():
            if self.label == label.name:
                return True
        return False
    
    def __unicode__(self):
        return "Project '%s' synchronised on repository '%s' with label '%s'"%(self.project, self.repository, self.label)
