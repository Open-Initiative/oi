#coding: utf-8
# Vues des utilisateurs
from django.http import HttpResponseRedirect,HttpResponse
from oi.users.models import UserProfile, UserProfileForm
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

@login_required
def userprofile(request):
    return render_to_response("userprofile.html",{'user':request.user})

@login_required
def editprofile(request):
    return render_to_response("editprofile.html",{'user':request.user,'form':UserProfileForm(instance=request.user.get_profile())})

@login_required
def saveprofile(request):
    form = UserProfileForm(request.POST, instance=request.user.get_profile())
    form.save()
    return HttpResponseRedirect(reverse('oi.users.views.userprofile'))
