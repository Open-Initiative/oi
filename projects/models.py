# coding: utf-8
# Modèles des projets
from django.db import models
from oi.settings import MEDIA_ROOT
from django.contrib.auth.models import User
from oi.messages.models import Message

# A project can contain subprojects and/or specs. Without them it is only a task
class Project(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, related_name='ownprojects', null=True, blank=True)
    assignee = models.ForeignKey(User, related_name='assigned_projects', null=True, blank=True)
    offer = models.DecimalField(max_digits= 12,decimal_places=2,default=0)
    message = models.ForeignKey(Message)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='tasks')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_specs(self):
        """Returns all the specs of the project"""
        return self.spec_set.order_by('order')
        
    def get_max_order(self):
        """Returns the position of the last spec of the project"""
        return self.spec_set.aggregate(maxorder=models.Max('order'))['maxorder'] or 0
        
    def insert_spec(self, order):
        """insert a spec at the given position"""
        for spec in self.spec_set.filter(order__gte=order):
            spec.order += 1
            spec.save()
            
    def is_simple_task(self):
        """A simple task is a project with no spec and no subproject"""
        return self.tasks.count() == 0 and self.spec_set.count() == 0
        
    def __unicode__(self):
        return "%s : %s"%(self.id, self.title)

# Aspec is a content of a project
class Spec(models.Model):
    #Different types
    TEXT_TYPE = 1
    IMAGE_TYPE = 2
    URL_TYPE = 3
    VIDEO_TYPE = 4
    DOC_TYPE = 5
    TYPES =  {TEXT_TYPE:"Texte", IMAGE_TYPE:"Image", URL_TYPE:"Lien url", VIDEO_TYPE:"Vidéo", DOC_TYPE:"Fichier joint"}
    
    author = models.ForeignKey(User, null=True, blank=True)
    project = models.ForeignKey(Project)
    type = models.IntegerField(choices=TYPES.items(), default=TEXT_TYPE)
    text = models.TextField()
    url = models.URLField(null=True, blank=True)
    file = models.FileField(upload_to="/home/lamp/tmp/",null=True, blank=True)
    image = models.ImageField(upload_to="/home/lamp/tmp/",null=True, blank=True)
    #~ content_type = models.CharField(max_length=100)
    order = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

# Offer of users on projets
class Bid(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User, related_name='bid_projects')
    amount = models.DecimalField(max_digits= 12,decimal_places=2)
    def __unicode__(self):
        return "%s : %s"%(self.user, self.amount)