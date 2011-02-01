# coding: utf-8
# Modèles des profils utilisateurs
from oi.projects.models import Project
from oi.messages.models import Message, Expert
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.forms import ModelForm, DateField
from django.forms.extras.widgets import SelectDateWidget
from notification import models as notification
from datetime import datetime

def getpicturepath(instance, filename):
    return "user/%s/%s"%(instance.user.username,filename)

# Extra data in the user profile
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    postcode = models.CharField(max_length=9, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)
    mobile = models.CharField(max_length=30, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    picture = models.ImageField(upload_to=getpicturepath,null=True, blank=True)
    contacts = models.ManyToManyField('self', symmetrical=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default="0.0")
    observed_messages = models.ManyToManyField(Message, related_name="followers", blank=True)
    observed_projects = models.ManyToManyField(Project, related_name="followers", blank=True)
    
    def get_titles(self):
        """suggests titles for the user, based on resume details"""
        #suggests any unfinished experience
        titles = map(lambda experience: u"%s chez %s"%(experience.job, experience.company),
            self.user.experience_set.filter(models.Q(end__isnull=True)|models.Q(end__gte=datetime.now())).order_by("-begining"))
        #adds the last finished job, if any
        try:
            titles.append(self.user.experience_set.filter(end__lte=datetime.now()).order_by("-end")[0].job)
        except IndexError:
            pass #if none, too bad
        #adds the current training if the user is a student
        titles.extend(map(lambda training: u"Etudiant en %s à %s"%(training.degree, training.university),
            self.user.training_set.filter(models.Q(end__isnull=True)|models.Q(end__gte=datetime.now())).order_by("-begining")))
        #adds all main skills
        titles.extend(map(lambda skill: u"Expert en %s"%skill.title,
            self.user.skill_set.filter(main=True)))
        return titles
        
    def make_payment(self, amount, project=None):
        """makes a new payment and updates user account"""
        payment = Payment(user=self.user, amount=amount, project=project)
        payment.save()
        self.balance += amount
        self.save()

    def last_projects(self):
        """returns the last five projects of the user, in which he participates, on which he bids, or which he created"""
        return Project.objects.filter(models.Q(assignee=self.user)|models.Q(bid__user=self.user)|models.Q(author=self.user)).order_by("-start_date")[:5]

    def last_messages(self):
        """returns the last five messages the user posted"""
        return self.user.ownmessages.order_by("-created")[:5]
    
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

    def msg_notify_all(self, msg, notice_type, param):
        """sends a notification to all users about this message"""
        recipients = User.objects.filter(userprofile__observed_messages__descendants = msg).exclude(userprofile=self)
        notification.send(recipients, notice_type, {'message':msg, 'param':param}, True, self.user)

    def prj_notify_all(self, prj, notice_type, param):
        """sends a notification to all users about this project"""
        recipients = User.objects.filter(userprofile__observed_projects__subprojects = prj).exclude(userprofile=self)
        notification.send(recipients, notice_type, {'project':prj, 'param':param}, True, self.user)

    def __unicode__(self):
        return "Profil de %s"%self.user

class Skill(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=100, blank=True)
    main = models.BooleanField(default=True)
    comment = models.TextField(blank=True)
    def __unicode__(self):
        return self.company

class Experience(models.Model):
    user = models.ForeignKey(User)
    begining = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    company = models.CharField(max_length=100, blank=True)
    job = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    def __unicode__(self):
        return self.company

class Training(models.Model):
    user = models.ForeignKey(User)
    begining = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    degree = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=100, blank=True)
    comment = models.TextField(blank=True)
    def __unicode__(self):
        return self.university

#Transaction from a user account
class Payment(models.Model):
    user = models.ForeignKey(User)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, blank=True)
    def __unicode__(self):
        return "%s on %s's account"%(self.amount,self.user)

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user','contacts','balance')

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
        instance.userprofile_set.add(UserProfile())

# Sets the profile on user creation
post_save.connect(set_profile, sender=User)
