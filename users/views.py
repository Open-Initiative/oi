#coding: utf-8
# Vues des utilisateurs
import os
from random import random
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.mail import send_mail
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template
from django.db.models import get_app, Count, Avg
from django.db import IntegrityError
from notification import models as notification
from oi.settings import MEDIA_ROOT, MEDIA_URL
from oi.helpers import render_to_pdf
from oi.users.models import User, UserProfile, UserProfileForm,  PersonalMessage
from oi.users.models import Training, TrainingForm, Experience, ExperienceForm, Skill, SkillForm, OI_USERPROFILE_DETAILS_CLASSES
from oi.projects.models import Bid

@login_required
def myprofile(request):
    """shows the profile of the current user"""
    extra_context = {'selected_user':request.user}
    extra_context.update(Bid.objects.filter(project__assignee=request.user).aggregate(Count("rating"),Avg("rating")))
    return direct_to_template(request, template="users/profile/profile.html", extra_context = extra_context)

@login_required
def exportresume(request):
    """Exports the profile of the current user as pdf"""
    response = HttpResponse(render_to_pdf("users/profile/resume.html", {'selected_user':request.user}), mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=resume.pdf'
    return response

def userprofile(request, username):
    """shows the profile of the given user"""
    user = User.objects.get(username=username)
    extra_context={'selected_user':user}
    extra_context.update(Bid.objects.filter(project__assignee=user).aggregate(Count("rating"),Avg("rating")))
    return direct_to_template(request, template="users/profile/profile.html", extra_context = extra_context)

@login_required
def dashboard(request):
    """user customized dashboard"""
    return direct_to_template(request, template="users/dashboard.html")

@login_required
def invite(request, id):
    """adds a user as a contact of the current user"""
    request.user.get_profile().contacts.add(id)
    notification.send( [ User.objects.get(id=id) ], 'invitation', {}, True, request.user )
    return HttpResponse("Contact ajouté")

def resetpassword(request):
    """sends an e-mail to the user with a new password"""
    try:
        user = User.objects.get(username=request.POST["username"])
    except User.DoesNotExist:
        return direct_to_template(request, template="users/resetpwd.html", extra_context = {'message': "Le nom d'utilisateur n'existe pas."})
    if user.email != request.POST["email"]:
        return direct_to_template(request, template="users/resetpwd.html", extra_context = {'message': "L'adresse e-mail ne correspond pas."})
    password = User.objects.make_random_password()
    user.set_password(password)
    user.save()
    send_mail("Nouveau Mot de passe", "Votre mot de passe a été réinitialisé. Votre nouveau mot de passe est : %s"%password, "admin@open-initiative.com", [user.email])    
    return direct_to_template(request, template="users/resetpwd.html", extra_context = {'message': "Le nouveau mot de passe vous a été renvoyé par e-mail"})

@login_required
def changepassword(request):
    """updates user's password"""
    if not request.user.check_password(request.POST["oldpassword"]):
        return HttpResponse('Mot de passe incorrect !')
    if request.POST['newpassword'] != request.POST['confirmpassword']:
        return HttpResponse('Les mots de passe ne correspondent pas !')
    request.user.set_password(request.POST['newpassword'])
    request.user.save()
    return HttpResponse("Votre mot de passe a été mis à jour")

def createuser(request):
    """creates a new user"""
    if request.POST["password"] != request.POST["password_confirm"]:
        return render_to_response("users/register.html",{'message':"Les mots de passe ne correspondent pas."})
    try:
        user = User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password"])
    except IntegrityError:
        return render_to_response("users/register.html",{'message':"Ce nom d'utilisateur existe déjà !"})
    user.first_name = request.POST["firstname"]
    user.last_name = request.POST["lastname"]
    user.save()
    return HttpResponseRedirect(reverse('oi.users.views.myprofile'))

@login_required
def editdetail(request, id):
    """edit resume detail of the user"""
    type = request.GET["type"]
    #gets the classes corresponding to the detail type
    objclass,formclass = OI_USERPROFILE_DETAILS_CLASSES[type]    
    if id=='0': #new detail
        instance = objclass(user=request.user)
    else:
        instance = objclass.objects.get(id=id)

    divid = request.GET.get("divid")
    form = formclass(instance=instance, prefix=divid) #prefix form elements with divid to allow multiple edition at the same time
    return render_to_response("users/profile/editdetail.html",{'user':request.user,'id':id,'form':form,'divid':divid,'type':type})

@login_required
def savedetail(request, id):
    """saves a resume detail of the user"""
    type = request.POST["type"]
    #gets the classes corresponding to the detail type
    objclass,formclass = OI_USERPROFILE_DETAILS_CLASSES[type]
    if id=='0': #new detail
        instance = objclass(user=request.user)
    else:
        instance = objclass.objects.get(id=id)
    form = formclass(request.POST, instance=instance, prefix=request.POST['divid'])
    instance = form.save()
    return render_to_response("users/profile/%s.html"%type,{'user':request.user, type:instance, 'selected_user':request.user})
    
@login_required
def deletedetail(request, id):
    """deletes a detail from the user's resume"""
    type = request.POST["type"]
    #gets the classes corresponding to the detail type
    objclass,formclass = OI_USERPROFILE_DETAILS_CLASSES[type]
    detail = objclass.objects.get(id=id)
    if detail.user != request.user:
        return HttpResponse("Impossible de modifier le profil d'un autre utilisateur")
    detail.delete()
    return HttpResponse("Modification enregistrée")

@login_required
def setusertitle(request):
    """changes user's title"""
    request.user.get_profile().title = request.POST["title"]
    request.user.get_profile().save()
    return HttpResponse("Modification enregistrée")

@login_required
def setbirthdate(request):
    """changes user's birth date"""
    request.user.get_profile().birthdate = request.POST["date"]
    request.user.get_profile().save()
    return HttpResponse("Modification enregistrée")

@login_required
def uploadpicture(request):
    """changes user's profile picture"""
    if request.user.get_profile().picture:
        request.user.get_profile().picture.delete()
    request.user.get_profile().picture.save("profile.jpg", File(request.FILES['picture']))
    return HttpResponse("<script>window.parent.document.getElementById('user_picture').src += '?%s'</script>"%(random()))

def getpicture(request, username):
    """Downloads given user's profile picture"""
    if not User.objects.get(username=username).get_profile().picture:
        return HttpResponseRedirect('/img/user.png') #default picture
    response = HttpResponse(mimetype='image/jpeg')
    response['X-Sendfile'] = "%suser/%s/profile.jpg"%(MEDIA_ROOT,username)
    response['Content-Length'] = os.path.getsize("%suser/%s/profile.jpg"%(MEDIA_ROOT,username))
    return response

@login_required
def invoice(request):
    """Exports the invoice of all user payments as pdf"""
    response = HttpResponse(render_to_pdf("users/pdf/invoice.html", {'user':request.user}), mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=invoice.pdf'
    return response

@login_required
def sendMP(request, id):
    """sends a private to the selected user, from the current user"""
    mp = PersonalMessage(from_user=request.user, to_user=User.objects.get(id=id), text=request.POST['message'], subject=request.POST['subject'])
    mp.save()
    notification.send([mp.to_user], 'personal_message', {'message':mp.text, 'subject':mp.subject}, True, mp.from_user)
    return HttpResponse("Message envoyé")

@login_required
def getusermessages(request, username):
    """gets all messages with the user"""
    contact = User.objects.get(username=username)
    to_messages = PersonalMessage.objects.filter(from_user=contact).filter(to_user=request.user)
    from_messages = PersonalMessage.objects.filter(to_user=contact).filter(from_user=request.user)
    messages = (to_messages|from_messages).order_by('sent_date')
    return direct_to_template(request, template="users/usermessages.html", extra_context = {'contact':contact,'personalmessages':messages})
