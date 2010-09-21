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

notification = get_app( 'notification' )

@login_required
def myprofile(request):
    return direct_to_template(request, template="users/profile.html",extra_context={'selected_user':request.user})

def userprofile(request, username):
    return direct_to_template(request, template="users/profile.html",extra_context={'selected_user':User.objects.get(username=username)})

@login_required
def invite(request, id):
    request.user.get_profile().contacts.add(id)
    notification.send( [ User.objects.get(id=id) ], 'invitation', {}  )
    return HttpResponse("Contact ajouté")

@login_required
def editprofile(request):
    return render_to_response("users/editprofile.html",{'user':request.user,'form':UserProfileForm(instance=request.user.get_profile())})

def createuser(request):
    if request.POST["password"] != request.POST["password_confirm"]:
        return HttpResponse("Les mots de passe ne correspondent pas.")
    user = User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password"])
    user.save()
    return HttpResponseRedirect(reverse('oi.users.views.userprofile'))
    
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
    return HttpResponseRedirect(reverse('oi.users.views.userprofile'))

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
    notification.send( [ User.objects.get(id=id) ], 'message', {'message':mp}  )
    return HttpResponse("Message envoyé")
