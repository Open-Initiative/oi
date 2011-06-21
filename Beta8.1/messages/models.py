# coding: utf-8
# Modèles des messages
from math import copysign
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404
from oi.helpers import OI_SCORE_ANONYMOUS, OI_SCORE_DEFAULT_RELEVANCE, OI_SCORE_ADD, OI_SCORE_VOTE, OI_SCORE_FRACTION_TO_PARENT
from oi.helpers import OI_SCORE_FRACTION_FROM_PARENT, OI_EXPERTISE_TO_MESSAGE, OI_EXPERTISE_TO_AUTHOR, OI_EXPERTISE_FROM_ANSWER
from oi.helpers import OI_ALL_PERMS, OI_PERMS, OI_RIGHTS, OI_READ, OI_WRITE, OI_ANSWER

# Représentation du message
class Message(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, related_name='ownmessages', null=True, blank=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    icon = models.CharField(max_length=100, blank=True)
    category = models.BooleanField()
    rfp = models.BooleanField()
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    ancestors = models.ManyToManyField('self',symmetrical=False, related_name='descendants', blank=True)
    related = models.ManyToManyField('self',symmetrical=False, related_name='related_to', blank=True)
    relevance = models.FloatField()
    public = models.BooleanField()
    
    # surcharge la sauvegarde pour le calcul des ancetres
    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)
        self.ancestors = self.get_ancestors()
    
    # Lorsqu'un utilisateur vote pour un message
    def vote(self, user, opinion, ip_address):
        """Ajoute un vote de l'utilisateur sur le message
        opinion est positif ou négatif
        l'adresse ip est stockée pour empêcher les doubles votes anonymes
        """
        if self.has_voted(user, ip_address):
            return #Ne vote pas deux fois
        
        # Modifie la pertinence du message, en fonction de l'expertise de l'utilisateur
        self.relevance += copysign(self.get_expertise(user)*OI_EXPERTISE_TO_MESSAGE, opinion)
        # Augmente l'expertise de l'auteur, en fonction de l'expertise de l'utilisateur
        self.add_expertise(self.author, copysign(self.get_expertise(user)*OI_EXPERTISE_TO_AUTHOR, opinion))

        # Augmente l'expertise de l'utilisateur 
        if user.is_authenticated():
            self.add_expertise(user, OI_SCORE_VOTE, True) # Remonte l'expertise aux parent
        else:
            self.usedip_set.add(UsedIP(address=ip_address)) # Enregistre l'adresse ip pour éviter les doubles votes
    
    def get_projects(self):
        """Gets the projects of the message, excepted the sub-projects"""
        return self.project_set.filter(parent=None)
        
    def is_expert(self, user):
        """Returns true if the user has an expertise on that particular message"""
        return user.is_authenticated() and len(self.expert_set.filter(user=user))>0
    
    def has_voted(self, user, ip_address):
        """Tells if the user is allowed to vote on that message"""
        if user.is_anonymous():
            return len(self.usedip_set.filter(address=ip_address))>0
        else:
            return self.is_expert(user) and self.expert_set.filter(user=user)[0].voted
    
    def get_expertise(self, user):
        """Returns the expertise of user on the branch of the message"""
        if user.is_anonymous():
            return OI_SCORE_ANONYMOUS
            
        # Non expert and anonymous have the same score
        expertise = OI_SCORE_ANONYMOUS
        if self.is_expert(user):
            expertise = self.expert_set.filter(user=user)[0].score
        # Gets expertise from the whole branch, ie including parent
        if self.parent:
            expertise += self.parent.get_expertise(user)*OI_SCORE_FRACTION_FROM_PARENT
        return expertise
        
    def add_expertise(self, user, score, is_vote=False):
        """Adds expertise to that user on that particular message, and on parent
        If is_vote, prevents the user from voting twice"""
        if user==None or user.is_anonymous():
            return
            
        # If user already has expertise on that message
        if self.is_expert(user):
            expert = self.expert_set.filter(user=user)[0]
            expert.score += score
            if is_vote:
                expert.voted = True
            expert.save()
        else:
            expert = Expert(message=self, user=user, score=score+1., voted=is_vote)
            expert.save()
            self.expert_set.add(expert)
            
        # Adds fraction to parent, if score still high enough
        if score >= OI_SCORE_ANONYMOUS:
            if self.parent:
                self.parent.add_expertise(user,score*OI_SCORE_FRACTION_TO_PARENT)
    
    def has_perm(self, user, perm):
        """checks if the user has the required perms"""
        #superuser a tous les droits
        if user.is_superuser:
            return True
        if perm in [OI_READ, OI_ANSWER] and self.public:
            return True
        if user.is_anonymous():
            return False
        return len(self.messageacl_set.filter(user=user,permission=perm))>0
    
    def set_perm(self, user, perm):
        """adds the specified perm to the user"""
        if user and user.is_authenticated:
            if perm == OI_ALL_PERMS:
                for right in OI_RIGHTS:
                    self.messageacl_set.get_or_create(user=user, permission=right)
            else:
                self.messageacl_set.get_or_create(user=user, permission=perm)
    
    def get_ancestors(self):
        """returns all the paths to the message"""
        if self.parent:
            return self.parent.get_ancestors()+[self]
        else:
           return [self]

    def get_categories(self):
        """returns categories of which the message descents"""
        return self.ancestors.filter(category=True)
    
    def __unicode__(self):
        return "%s : %s"%(self.id, self.title)

#Structure de contrôle des permissions
class MessageACL(models.Model):
    user = models.ForeignKey(User)
    message = models.ForeignKey(Message)
    permission = models.IntegerField(choices=OI_PERMS)
    class Meta:
        unique_together = (("message", "user", "permission"),)
    def __unicode__(self):
        return "%s on %s : %s"%(self.user, self.message, self.permission)

#Décorateur de vérification de permissions
def OINeedsMsgPerms(*required_perms):
    def decorate(f):
        def new_f(request, id, *args, **kwargs):
            #Vérification de toutes les permissions
            msg = get_object_or_404(Message, pk=id)
            for perm in required_perms:
                if not msg.has_perm(request.user, perm):
                    if perm==OI_READ:
                        raise Http404
                    return HttpResponseForbidden(_("Forbidden"))
            return f(request, id, *args, **kwargs)
        return new_f
    return decorate 

# Ip qui a voté sur un message
class UsedIP(models.Model):
    address = models.CharField(max_length=40)
    message = models.ForeignKey(Message)
    def __unicode__(self):
        return "%s : %s"%(self.message, self.address)
    
# Utilisateur ayant une expertise sur un message, et/ou ayant voté pour ce message
class Expert(models.Model):
    message = models.ForeignKey(Message)
    user = models.ForeignKey(User, related_name='specialties')
    score = models.FloatField()
    voted = models.BooleanField()
    def __unicode__(self):
        return "%s : %s"%(self.user, self.message.title)
        
# Contenu éditorial
class PromotedMessage(models.Model):
    message = models.ForeignKey(Message)
    location = models.CharField(max_length=50)
    def __unicode__(self):
        return "%s(%s)"%(self.message.title, self.location)
