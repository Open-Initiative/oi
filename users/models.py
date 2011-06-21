# coding: utf-8
# Modèles des profils utilisateurs
import logging
from decimal import Decimal
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.forms import ModelForm, DateField
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy, ugettext as _
from oi.notification import models as notification
from oi.settings import SHASIGN_NAME
from oi.helpers import OI_DISPLAYNAME_TYPES, computeSHA
from oi.messages.models import Message, Expert
from oi.projects.models import Project, Bid

def getpicturepath(instance, filename):
    return "user/%s/%s"%(instance.user.username,filename)

# Extra data in the user profile
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
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
    rss_feed = models.URLField(verify_exists=False, blank=True)
    last_feed = models.DateTimeField(null=True, blank=True)
    observed_messages = models.ManyToManyField(Message, related_name="followers", blank=True)
    observed_projects = models.ManyToManyField(Project, related_name="followers", blank=True)
    
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
        shasign = info.pop(SHASIGN_NAME) #remove the signature from the info
        if shasign != computeSHA(info): #invalid SHA signature
            logger.error("Signature SHA incorrecte : %s"%shasign)
            return
        if self.user != payment.user: #the user originating the request is not the owner of the payment
            logger.error("Mauvais utilisateur : (%s, %s)"%(self.user.username, payment.user.username))
            return
        if info['STATUS']=='5' or info['STATUS']=='51' or info['STATUS']=='52' or info['STATUS']=='91' or info['STATUS']=='92':
            logger.warning("Paiement %s non validé : %s"%(payment.id,info['STATUS'].__str__()))
            return #codes indicating the payment is awaiting completion

        if info['STATUS']=='9':
            profile = payment.user.get_profile()
            profile.balance -= payment.amount #remove old amount from balance before updating account
            payment.amount = Decimal(info['amount'])
            profile = payment.user.get_profile()
            profile.balance += payment.amount
            profile.save()
            payment.reason = _("online payment")
            logger.info(_("Paiement %s validated")%payment.id)
        else:
            payment.reason = "Paiement en ligne annulé"
            logger.warning("Paiement %s non validé : %s"%(payment.id,info['STATUS'].__str__()))
        payment.save()

    def followed_rfp(self):
        """returns all rfp followed by the user"""
        return self.observed_messages.filter(rfp=True)
    
    def get_message_updates(self):
        """gets modified messages descendants of user's best expertised messages"""
        return Message.objects.filter(ancestors__expert__user=self.user).filter(category=False).distinct().order_by("-modified")
        
    def get_project_updates(self):
        """gets modified projects inside user's user's best expertised messages"""
        return Project.objects.filter(message__ancestors__expert__user=self.user).distinct().order_by("-modified")
        
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

    def msg_notify_all(self, msg, notice_type, param):
        """sends a notification to all users about this message"""
        recipients = User.objects.filter(userprofile__observed_messages__descendants = msg).exclude(userprofile=self).distinct()
        notification.send(recipients, notice_type, {'message':msg, 'param':param}, True, self.user)

    def prj_notify_all(self, prj, notice_type, param):
        """sends a notification to all users about this project"""
        recipients = User.objects.filter(userprofile__observed_projects__subprojects = prj).exclude(userprofile=self).distinct()
        notification.send(recipients, notice_type, {'project':prj, 'param':param}, True, self.user)

    def __unicode__(self):
        return self.get_display_name()

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
    def __unicode__(self):
        return self.company

class Training(models.Model):
    user = models.ForeignKey(User)
    begining = models.DateField(null=True, blank=True, verbose_name=ugettext_lazy("Begining"))
    end = models.DateField(null=True, blank=True, verbose_name=ugettext_lazy("End"))
    degree = models.CharField(max_length=100, blank=True, verbose_name=ugettext_lazy("Degree"))
    university = models.CharField(max_length=100, blank=True, verbose_name=ugettext_lazy("University"))
    comment = models.TextField(blank=True, verbose_name=ugettext_lazy("Comment"))
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
        fields = ('address','postcode','city','country','mobile','phone')

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
        instance.userprofile_set.add(UserProfile(blog=Message.objects.create(author=instance, relevance=1, public=True, title=_("%s's blog")%instance.username)))
        instance.get_profile().observed_messages.add(instance.get_profile().blog)

# Sets the profile on user creation
post_save.connect(set_profile, sender=User)
