# coding: utf-8
# Modèles des messages
from django.db import models
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from math import copysign

# Constantes de transmission de pertinence
OI_SCORE_ANONYMOUS = 1. #Score du vote anonyme
OI_SCORE_DEFAULT_RELEVANCE = 10. #Pertinence par défaut des messages
OI_SCORE_ADD = 3. #Score au contributeur
OI_SCORE_VOTE = 2. #Score au votant
OI_SCORE_FRACTION_TO_PARENT = .5 #Fraction montante
OI_SCORE_FRACTION_FROM_PARENT = .5 #Fraction descendante
OI_EXPERTISE_TO_MESSAGE = .02 #Transmission d'expertise au message
OI_EXPERTISE_TO_AUTHOR = .02 #Transmission d'expertise à l'auteur
OI_EXPERTISE_FROM_ANSWER = .002 #Fraction transmise par une réponse

# Représentation du message
class Message(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, related_name='ownmessages', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    icon = models.CharField(max_length=100, blank=True)
    category = models.BooleanField()
    text = models.TextField()
    parents = models.ManyToManyField('self',symmetrical=False, related_name='children', blank=True)
    ancestors = models.ManyToManyField('self',symmetrical=False, related_name='descendants', blank=True)
    relevance = models.FloatField()
    public = models.BooleanField()
    
    # surcharge la sauvegarde pour le calcul des ancetres
    def save(self):
        super(Message, self).save()
        for line in self.get_ancestors():
            for ancestor in line:
                self.ancestors.add(ancestor)
    
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
            self.add_expertise(user, OI_SCORE_VOTE, True) # Remonte l'expertise aux messages parents
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
        # Gets expertise from the whole branch, ie including parents
        for parent in self.parents.all():
            expertise += parent.get_expertise(user)*OI_SCORE_FRACTION_FROM_PARENT
        return expertise
        
    def add_expertise(self, user, score, is_vote=False):
        """Adds expertise to that user on that particular message, and on parents
        If is_vote, prevents the user from voting twice
        """
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
            
        # Adds fraction to parents, if score still high enough
        if score >= OI_SCORE_ANONYMOUS:
            for parent in self.parents.all():
                parent.add_expertise(user,score*OI_SCORE_FRACTION_TO_PARENT)
    
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
                    self.messageacl_set.add(MessageACL(user=user, permission=right))
            else:
                self.messageacl_set.add(MessageACL(user=user, permission=perm))
    
    def get_ancestors(self):
        """returns all the paths to the message"""
        if self.parents.count()==0:
            return [[self]]
        ancestors=[]
        #makes a list of all paths to all parents
        for parent in self.parents.all():
            for path in parent.get_ancestors():
                ancestors.append(path+[self])        
        return ancestors
    
    def get_children(self):
        return self.children.order_by("-relevance")
    
    def __unicode__(self):
        return "%s : %s"%(self.id, self.title)

#Liste des permissions sur les messages
OI_ALL_PERMS = -1
OI_RIGHTS = [OI_READ, OI_WRITE, OI_ANSWER] = [1,2,4]
OI_MSG_PERMS = ((OI_READ, "Lecture"), (OI_WRITE, "Ecriture"), (OI_ANSWER, "Réponse"),) 

#Structure de contrôle des permissions
class MessageACL(models.Model):
    user = models.ForeignKey(User)
    message = models.ForeignKey(Message)
    permission = models.IntegerField(choices=OI_MSG_PERMS)
    def __unicode__(self):
        return "%s on %s : %s"%(self.user, self.message, self.permission)

#Décorateur de vérification de permissions
def OINeedsMsgPerms(*required_perms):
    def decorate(f):
        def new_f(request, id, *args, **kwargs):
            #Vérification de toutes les permissions
            msg = Message.objects.get(id=id)
            for perm in required_perms:
                if not msg.has_perm(request.user, perm):
                    return HttpResponseForbidden("Permissions insuffisantes")
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
