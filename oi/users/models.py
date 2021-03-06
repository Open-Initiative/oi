# coding: utf-8
# Modèles des profils utilisateurs
import logging
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.forms import ModelForm, DateField, PasswordInput
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy, ugettext as _, get_language
from oi.helpers import OI_DISPLAYNAME_TYPES, computeSHA
from oi.messages.models import Message, Expert
from oi.projects.models import Project, Bid
from oi.prjnotify.models import Observer

def getpicturepath(instance, filename):
    return "user/%s/%s"%(instance.user.username,filename)

# Extra data in the user profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", unique=True)
    birthdate = models.DateField(null=True, blank=True, verbose_name=ugettext_lazy("Birthdate"))
    address = models.CharField(max_length=200, blank=True, verbose_name=ugettext_lazy("Address"))
    postcode = models.CharField(max_length=9, blank=True, verbose_name=ugettext_lazy("Post Code"))
    city = models.CharField(max_length=50, blank=True, verbose_name=ugettext_lazy("City"))
    country = models.CharField(max_length=30, blank=True, verbose_name=ugettext_lazy("Country"))
    mobile = models.CharField(max_length=30, blank=True, verbose_name=ugettext_lazy("Mobile"))
    phone = models.CharField(max_length=30, blank=True, verbose_name=ugettext_lazy("Phone Number"))
    title = models.CharField(max_length=100, blank=True)
    display_name = models.IntegerField(default=0)
    picture = models.ImageField(upload_to=getpicturepath,null=True, blank=True)
    language = models.CharField(max_length=10, default='fr')
    contacts = models.ManyToManyField('self', symmetrical=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default="0.0")
    blog = models.ForeignKey(Message, unique=True)
    rss_feed = models.URLField(blank=True)
    last_feed = models.DateTimeField(null=True, blank=True)
    personal_website = models.URLField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True)
    github_username = models.CharField(max_length=100, blank=True, null=True)
    github_password = models.CharField(max_length=100, blank=True, null=True)
    tax_rate = models.DecimalField(max_digits= 12, decimal_places=2, blank=True, null=True)
    contacted = models.BooleanField(default=False)
    
    def get_titles(self):
        """suggests titles for the user, based on resume details"""
        #suggests any unfinished experience
        titles = map(lambda experience: _(u"%(job)s at %(company)s")%{'job':experience.job, 'company':experience.company},
            self.user.experience_set.filter(models.Q(end__isnull=True)|models.Q(end__gte=datetime.now())).order_by("-begining"))
        #adds the last finished job, if any
        try:
            titles.append(self.user.experience_set.filter(end__lte=datetime.now()).order_by("-end")[0].job)
        except IndexError:
            pass #if none, too bad
        #adds the current training if the user is a student
        titles.extend(map(lambda training: _(u"Studying %(degree)s in %(university)s")%{'degree':training.degree, 'university':training.university},
            self.user.training_set.filter(models.Q(end__isnull=True)|models.Q(end__gte=datetime.now())).order_by("-begining")))
        #adds all main skills
        titles.extend(map(lambda skill: _(u"Expert in %(skill)s")%{'skill':skill.title},
            self.user.skill_set.filter(main=True)))
        return titles
    
    def get_display_name(self):
        """displays the user full name as desired"""
        return OI_DISPLAYNAME_TYPES[self.display_name]%{'username':self.user.username, 'first':self.user.first_name, 'last':self.user.last_name}
    
    def make_payment(self, amount, reason, project=None):
        """makes a new payment and updates user account"""
        if amount==0:
            return
        payment = Payment(user=self.user, amount=amount, reason=reason, project=project)
        payment.save()
        self.balance += amount
        self.save()
    
    def update_payment(self, info):
        """updates the payment with information received from payment service provider"""
        logger = logging.getLogger('oi.payments')
        logger.info(info)
        payment = Payment.objects.get(id=info['orderID'])
        shasign = info.pop(settings.SHASIGN_NAME) #remove the signature from the info
        if shasign != computeSHA(info): #invalid SHA signature
            logger.error("Signature SHA incorrecte : %s"%shasign)
            return False
        if self.user != payment.user: #the user originating the request is not the owner of the payment
            logger.error("Mauvais utilisateur : (%s, %s)"%(self.user.username, payment.user.username))
            return False
        if info['STATUS']=='5' or info['STATUS']=='51' or info['STATUS']=='52' or info['STATUS']=='91' or info['STATUS']=='92':
            logger.warning("Paiement %s non validé : %s"%(payment.id,info['STATUS'].__str__()))
            return False #codes indicating the payment is awaiting completion

        if info['STATUS']=='9':
            #remove old amount from balance before updating account
            delta =  Decimal(info['amount']) - payment.amount
            self.balance += delta 
            self.save()

            payment.amount += delta
            payment.reason = _("online payment")
            logger.info(_("Paiement %s validated")%payment.id)
        else:
            payment.reason = "Paiement en ligne annulé"
            logger.warning("Paiement %s non validé : %s"%(payment.id,info['STATUS'].__str__()))
            delta = 0
        payment.save()
        #delta is the amount actually added, considering this function can be called several times
        #the second time, delta is probably 0
        return delta

    def get_message_updates(self):
        """gets modified messages descendants of user's best expertised messages"""
        return Message.objects.filter(ancestors__expert__user=self.user).filter(category=False).distinct().order_by("-modified")
        
    def get_categories(self):
        """returns the categories in which the user has most expertise"""
        return map(lambda xp : xp.message, Expert.objects.filter(message__category=True).filter(user=self.user).order_by("-score")[:3])
        
    def get_discussions(self):
        """Returns last messages sent to the user"""
        users = User.objects.filter(sent__to_user=self).annotate(last_sent=models.Max("sent__sent_date")).order_by("-last_sent")
        # TODO find a better way
        return map(lambda user: PersonalMessage.objects.filter(from_user=user).filter(to_user=self).order_by("-sent_date")[0], users)

    def get_comments(self):
        """Returns comments made in evals on the user"""
        return Bid.objects.filter(project__assignee=self.user).exclude(comment="")

    def get_default_observer(self, prj=None):
        """gets the observer that applies for notification when no project is provided"""
        if Observer.objects.filter(user=self.user, project__descendants=prj):
            return Observer.objects.filter(user=self.user, project__descendants=prj)[0]
        observer, created = Observer.objects.get_or_create(user=self.user, project=None, use_default=False)
        return observer
        
    def get_observed_projects(self):
        """ filter all projects followed by the user and exclude all promoted project"""
        return Project.objects.filter(observer__user=self.user).exclude(promotedproject__isnull=False)
    
    def get_created_projects(self):
        """ filter all projects created by the user, excluding tasks"""
        return self.user.ownprojects.filter(parent=None)
    
    def get_funded_projects(self):
        """ filter all projects in which the user has a bid on a task"""
        return Project.objects.filter(subprojects__bid__user=self.user).distinct()
    
    def follow_project(self, project):
        """make the user follow the project"""
        if Observer.objects.filter(user=self.user, project__descendants=project):
            return False
        else:
            Observer.objects.get_or_create(user=self.user, project=project)
            return True
        
    def unfollow_project(self, project):
        """make the user stop following the project"""
        for observer in Observer.objects.filter(user=self.user, project__descendants=project):
            observer.delete()
        if Observer.objects.filter(user=self.user, project=project):
            Observer.objects.get(user=self.user, project=project).delete()

    def __unicode__(self):
        return self.get_display_name()

class DetailsManager(models.Manager):
    def with_start_date(self):
        """includes only traning or experience with start date"""
        return self.filter(begining__isnull=False)
    
    def with_no_start_date(self):
        """includes only traning or experience with no start date"""
        return self.filter(begining__isnull=True)

class Skill(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=100, blank=True, verbose_name=ugettext_lazy("Title"))
    main = models.BooleanField(default=True, verbose_name=ugettext_lazy("Main skill"))
    comment = models.TextField(blank=True, verbose_name=ugettext_lazy("Comment"))
    def __unicode__(self):
        return self.company

class Experience(models.Model):
    user = models.ForeignKey(User)
    begining = models.DateField(null=True, blank=True, verbose_name=ugettext_lazy("Begining"))
    end = models.DateField(null=True, blank=True, verbose_name=ugettext_lazy("End"))
    company = models.CharField(max_length=100, blank=True, verbose_name=ugettext_lazy("Company"))
    job = models.CharField(max_length=100, blank=True, verbose_name=ugettext_lazy("Job"))
    description = models.TextField(blank=True, verbose_name=ugettext_lazy("Description"))
    objects = DetailsManager()
    def __unicode__(self):
        return self.company

class Training(models.Model):
    user = models.ForeignKey(User)
    begining = models.DateField(null=True, blank=True, verbose_name=ugettext_lazy("Begining"))
    end = models.DateField(null=True, blank=True, verbose_name=ugettext_lazy("End"))
    degree = models.CharField(max_length=100, blank=True, verbose_name=ugettext_lazy("Degree"))
    university = models.CharField(max_length=100, blank=True, verbose_name=ugettext_lazy("University"))
    comment = models.TextField(blank=True, verbose_name=ugettext_lazy("Comment"))
    objects = DetailsManager()
    def __unicode__(self):
        return self.university

#Transaction from a user account
class Payment(models.Model):
    user = models.ForeignKey(User)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    reason = models.CharField(max_length=200)
    transaction_date = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, blank=True, null=True)
    def __unicode__(self):
        return "%s on %s's account"%(self.amount,self.user)

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('address','postcode','city','country','mobile','phone','personal_website')

class SkillForm(ModelForm):
    class Meta:
        model = Skill
        exclude = ('user',)

class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        exclude = ('user',)

class TrainingForm(ModelForm):
    class Meta:
        model = Training
        exclude = ('user',)

class Prospect(models.Model):
    email = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    contacted = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    kompassId = models.CharField(max_length=20)

OI_USERPROFILE_DETAILS_CLASSES = {"experience":(Experience,ExperienceForm), "training":(Training,TrainingForm), "skill":(Skill,SkillForm)}

class PersonalMessage(models.Model):
    from_user = models.ForeignKey(User, related_name='sent')
    to_user = models.ForeignKey(User, related_name='received')
    subject = models.CharField(max_length=100)
    text = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return "%s to %s : %s"%(self.from_user, self.to_user, self.subject)
        
    # Sets the UserProfile class to be the profile of the given django User class
    def set_profile(sender, instance, created, **kwargs):
        if created==True:
            profile = UserProfile(user=instance, language=get_language())
            blog = Message(author=instance, relevance=1, title=_("%s's blog")%instance.username)
            blog.save()
            profile.blog = blog
            profile.save()
            
    # Sets the profile on user creation
    post_save.connect(set_profile, sender=User)
