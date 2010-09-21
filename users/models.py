# coding: utf-8
# Modèles des profils utilisateurs
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Extra data in the user profile
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    birthdate = models.DateField(null=True, blank=True)
    contacts = models.ManyToManyField('self', symmetrical=True, blank=True)
    def __unicode__(self):
        return "Profil de %s"%self.user

class Experience(models.Model):
    user = models.ForeignKey(User)
    begining = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    company = models.CharField(max_length=100, blank=True)
    job = models.CharField(max_length=100, blank=True)
    def __unicode__(self):
        return self.company

class Training(models.Model):
    user = models.ForeignKey(User)
    begining = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    degree = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=100, blank=True)
    def __unicode__(self):
        return self.university

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        exclude = ('user',)

class TrainingForm(ModelForm):
    class Meta:
        model = Training
        exclude = ('user',)

class PersonalMessage(models.Model):
    from_user = models.ForeignKey(User, related_name='sent')
    to_user = models.ForeignKey(User, related_name='received')
    subject = models.CharField(max_length=100)
    text = models.TextField()

# Sets the UserProfile class to be the profile of the given django User class
def set_profile(sender, instance, created, **kwargs):
    if created==True:
        instance.userprofile_set.add(UserProfile())

# Sets the profile on user creation
post_save.connect(set_profile, sender=User)
