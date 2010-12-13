#coding: utf-8
# Vues des utilisateurs
from oi.users.models import User, UserProfile, UserProfileForm, Training, TrainingForm, Experience, ExperienceForm, PersonalMessage
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.db.models import get_app
from django.db import IntegrityError
from django.core.mail import send_mail

notification = get_app( 'notification' )

@login_required
def myprofile(request):
    return direct_to_template(request, template="users/profile.html",extra_context={'selected_user':request.user})

def userprofile(request, username):
    return direct_to_template(request, template="users/profile.html",extra_context={'selected_user':User.objects.get(username=username)})

@login_required
def invite(request, id):
    request.user.get_profile().contacts.add(id)
    notification.send( [ User.objects.get(id=id) ], 'invitation', {"contact":request.user}  )
    return HttpResponse("Contact ajouté")

@login_required
def editprofile(request):
    return render_to_response("users/editprofile.html",{'user':request.user,'form':UserProfileForm(instance=request.user.get_profile())})

def resetpassword(request):
    user = User.objects.get(username=request.POST["username"])
    if user.email != request.POST["email"]:
        return HttpResponse("L'adresse e-mail ne correspond pas !")
    password = User.objects.make_random_password()
    user.set_password(password)
    user.save()
    send_mail("Nouveau Mot de passe", "Votre mot de passe a été réinitialisé. Votre nouveau mot de passe est : %s"%password, "admin@open-initiative.com", [user.email])    
    return HttpResponse("Le nouveau mot de passe vous a été renvoyé par e-mail")

@login_required
def changepassword(request):
    if not request.user.check_password(request.POST["oldpassword"]):
        return HttpResponse('Mot de passe incorrect !')
    if request.POST['newpassword'] != request.POST['confirmpassword']:
        return HttpResponse('Les mots de passe ne correspondent pas !')
    request.user.set_password(request.POST['newpassword'])
    request.user.save()
    return HttpResponse("Votre mot de passe a été mis à jour")

def createuser(request):
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
def edittraining(request, id):
    if id=='0':
        instance = Training(user=request.user)
    else:
        instance = Training.objects.get(id=id)
    return render_to_response("users/edittraining.html",{'user':request.user,'id':id,'form':TrainingForm(instance=instance)})

@login_required
def editexperience(request, id):
    if id=='0':
        instance = Experience(user=request.user)
    else:
        instance = Experience.objects.get(id=id)
    return render_to_response("users/editexperience.html",{'user':request.user,'id':id,'form':ExperienceForm(instance=instance)})

@login_required
def saveprofile(request):
    form = UserProfileForm(request.POST, instance=request.user.get_profile())
    form.save()
    request.user.last_name = request.POST.get("lastname")
    request.user.first_name = request.POST.get("firstname")
    request.user.save()
    return HttpResponseRedirect(reverse('oi.users.views.myprofile'))

@login_required
def savetraining(request, id):
    if id=='0':
        instance = Training(user=request.user)
    else:
        instance = Training.objects.get(id=id)
    form = TrainingForm(request.POST, instance=instance)
    form.save()
    return HttpResponseRedirect(reverse('oi.users.views.userprofile'))

@login_required
def saveexperience(request, id):
    if id=='0':
        instance = Experience(user=request.user)
    else:
        instance = Experience.objects.get(id=id)
    form = ExperienceForm(request.POST, instance=instance)
    form.save()
    return HttpResponseRedirect(reverse('oi.users.views.userprofile'))

@login_required
def sendMP(request, id):
    mp = PersonalMessage(from_user=request.user, to_user=User.objects.get(id=id), text=request.POST['message'], subject=request.POST['subject'])
    mp.save()
    notification.send( [ User.objects.get(id=id) ], 'message', {'message':mp.text, 'sender':mp.from_user, 'subject':mp.subject}  )
    return HttpResponse("Message envoyé")
