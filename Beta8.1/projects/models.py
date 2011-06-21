# coding: utf-8
# Modèles des projets
from datetime import datetime
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext as _
from oi.settings import MEDIA_ROOT
from oi.helpers import OI_ALL_PERMS, OI_PERMS, OI_RIGHTS, OI_READ, OI_WRITE, OI_ANSWER, OI_COMMISSION, OI_COM_ON_BID
from oi.helpers import OI_PRJ_STATES, OI_PROPOSED, OI_ACCEPTED, OI_STARTED, OI_DELIVERED, OI_VALIDATED, OI_CANCELLED, OI_POSTPONED, OI_CONTENTIOUS
from oi.helpers import SPEC_TYPES, TEXT_TYPE
from oi.messages.models import Message

# A project can contain subprojects and/or specs. Without them it is only a task
class Project(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, related_name='ownprojects', null=True, blank=True)
    assignee = models.ForeignKey(User, related_name='assigned_projects', null=True, blank=True)
    delegate_to = models.ForeignKey(User, related_name='delegated_projects', null=True, blank=True)    
    offer = models.DecimalField(max_digits= 12,decimal_places=2,default=0)
    commission = models.DecimalField(max_digits= 12,decimal_places=2,default=0)
    message = models.ForeignKey(Message)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='tasks')
    master = models.ForeignKey('self', blank=True, null=True, related_name='subprojects')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    delay = models.DateTimeField(blank=True, null=True)
    progress = models.FloatField(default=0.0)
    priority = models.IntegerField(default=0)
    state = models.IntegerField(choices=OI_PRJ_STATES)
    public = models.BooleanField(default=True)
    
    # overloads save to compute master project
    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
        if not self.master:
            parent = self
            while parent.parent:
                parent = parent.parent
            self.master = parent
            super(Project, self).save(*args, **kwargs)

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
        """A simple task is a project with no spec and no subproject"""
        return self.progress < 1.0 and self.due_date < datetime.now()
    
    def has_perm(self, user, perm):
        """checks if the user has the required perms"""
        #superuser always has all permissions
        if user.is_superuser:
            return True
        if perm in [1,4] and self.public:
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

    def canceled_bids(self):
        """gets all the bids marked as canceled"""
        return self.bid_set.filter(rating=-1)
    
    def is_bidder(self, user):
        return user.is_authenticated() and self.bid_set.filter(user=user).filter(rating=None).count() > 0

    def tasksbid_sum(self):
        """sums up all bids on the project's tasks"""
        return self.tasks.aggregate(models.Sum("bid__amount"))["bid__amount__sum"] or 0
        
    def tasksoffer_sum(self):
        """sums up all offers on the project's tasks"""
        return self.tasks.aggregate(models.Sum("offer"))["offer__sum"] or 0
        
    def bid_sum(self):
        """returns the sum of all bids on this project"""
        return self.bid_set.aggregate(models.Sum("amount"))["amount__sum"] or 0
    
    def missing_bid(self):
        """returns how much the project still needs to be started"""
        return max((self.offer*OI_COMMISSION) - self.bid_sum(), Decimal("0"))
    
    def finished_tasks(self):
        """gets all the tasks which state is at least delivered"""
        return self.tasks.filter(state__gte = OI_DELIVERED)

    def get_ancestors(self):
        """get message ancestors of the project"""
        return self.message.get_ancestors()

    def get_path(self):
        """get the location of the task inside the project"""
        if self.parent:
            return self.parent.get_path() + [self]
        else:
            return [self]

    def get_categories(self):
        return self.message.ancestors.filter(category=True)
    
    def is_ready_to_start(self):
        """returns True if the project is not started yet, has an assignee and enough bids"""
        if self.assignee is None:
            return False
        if self.state > OI_ACCEPTED:
            return False
        missing_bid = self.missing_bid()
        return missing_bid.is_signed() or missing_bid.is_zero()
    
    def reset_delay_request(self):
        """Remove the delay and resets user ratings"""    
        for bid in self.bid_set.all(): #reset all 
            bid.rating = None
            bid.save()
        self.delay = None
        self.save()

    def __unicode__(self):
        return "%s : %s"%(self.id, self.title)

#Structure de contrôle des permissions
class ProjectACL(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    permission = models.IntegerField(choices=OI_PERMS)
    class Meta:
        unique_together = (("project", "user", "permission"),)
    def __unicode__(self):
        return "%s on %s: %s"%(self.user, self.project, self.permission)

#Décorateur de vérification de permissions
def OINeedsPrjPerms(*required_perms):
    def decorate(f):
        def new_f(request, id, *args, **kwargs):
            #Vérification de toutes les permissions
            prj = Project.objects.get(id=id)
            for perm in required_perms:
                if not prj.has_perm(request.user, perm):
                    return HttpResponseForbidden(_("Forbidden"))
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
    text = models.TextField()
    url = models.URLField(null=True, blank=True)
    file = models.FileField(upload_to=getpath,null=True, blank=True)
    image = models.ImageField(upload_to=getpath,null=True, blank=True)
    order = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    #saves project as well
    def save(self):
        self.project.save()
        super(Spec, self).save()   

# Offer of users on projets
class Bid(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User, related_name='bid_projects')
    amount = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    validated = models.BooleanField(default=False)
    rating = models.IntegerField(null=True)
    comment = models.TextField()

    def cancel(self):
        """Cancels the bid : reimburses the bidder, reduces project offer, and deletes the bid"""
        amount = self.amount - self.amount*OI_COM_ON_BID #don't reimburse the commission part of the bid
        self.project.offer -= amount
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
