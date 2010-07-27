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
    def __unicode__(self):
        return "Profil de %s"%self.user

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

# Sets the UserProfile class to be the profile of the given django User class
def set_profile(sender, instance, created, **kwargs):
    if created==True:
        instance.userprofile_set.add(UserProfile())

# Sets the profile on user creation
post_save.connect(set_profile, sender=User)