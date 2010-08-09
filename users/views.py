#coding: utf-8
# Vues des utilisateurs
from django.http import HttpResponseRedirect,HttpResponse
from oi.users.models import UserProfile, UserProfileForm, Training, TrainingForm, Experience, ExperienceForm
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

@login_required
def userprofile(request):
    return render_to_response("users/userprofile.html",{'user':request.user})

@login_required
def editprofile(request):
    return render_to_response("users/editprofile.html",{'user':request.user,'form':UserProfileForm(instance=request.user.get_profile())})

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
