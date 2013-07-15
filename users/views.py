#coding: utf-8
# Vues des utilisateurs
import os, re
from random import random
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import get_app, Count, Avg
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.simplejson import JSONEncoder, JSONDecoder
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from oi.prjnotify.models import Notice, NoticeType, Observer
from oi.settings import MEDIA_ROOT, MEDIA_URL, PAYMENT_ACTION
from oi.helpers import render_to_pdf, OI_DISPLAYNAME_TYPES, computeSHA
from oi.users.models import User, UserProfile, UserProfileForm, PersonalMessage, Payment
from oi.users.models import Training, TrainingForm, Experience, ExperienceForm, Skill, SkillForm, OI_USERPROFILE_DETAILS_CLASSES
from oi.projects.models import Bid, Project

@login_required
def myprofile(request):
    """shows the profile of the current user"""
    extra_context = {'selected_user':request.user}
    extra_context.update(Bid.objects.filter(project__assignee=request.user).aggregate(Count("rating"),Avg("rating")))
    return direct_to_template(request, template="users/profile/profile.html", extra_context = extra_context)

@login_required
def exportresume(request, username):
    """Exports the profile of the current user as pdf"""
    response = HttpResponse(render_to_pdf("users/profile/resume.html", {'selected_user':User.objects.get(username=username)}), mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=resume.pdf'
    return response

def userprofile(request, username):
    """shows the profile of the given user"""
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404
    extra_context={'selected_user':user}
    extra_context.update(Bid.objects.filter(project__assignee=user).aggregate(Count("rating"),Avg("rating")))
    return direct_to_template(request, template="users/profile/profile.html", extra_context = extra_context)

@login_required
def myaccount(request):
    """user settings page"""
    if request.GET.get("orderID"):
        request.user.get_profile().update_payment(dict(request.GET.items())) #to obtain a mutable version of the QueryDict
    extra_context={'contact_form':UserProfileForm(instance=request.user.get_profile())}
    return direct_to_template(request, template='users/myaccount.html', extra_context=extra_context)

@login_required
def setemailing(request):
    """sets email sending for a given notice type for the current user"""
    notice_type = NoticeType.objects.get(label=request.POST["label"])
    send = (request.POST["send"] == "true")
    setting = Observer.objects.get(request.user).get_setting.update(send=send)
    return HttpResponse(_("Setting saved"))

@login_required
def savename(request):
    """saves user contact information"""
    request.user.last_name = request.POST['lastname']
    request.user.first_name = request.POST['firstname']
    request.user.save()
    return HttpResponse(_("Name saved"))

@login_required
def savecontactinfo(request):
    """saves user contact information"""
    form = UserProfileForm(request.POST, instance=request.user.get_profile())
    form.save()
    return HttpResponse(_("Information saved"))

@login_required
def setrss(request):
    """saves rss feed url into user's profile"""
    profile = request.user.get_profile()
    profile.rss_feed = request.POST["rss"]
    profile.save()
    return HttpResponse("Feed url saved")

@login_required
def invite(request, username):
    """adds a user as a contact of the current user"""
    user = User.objects.get(username = username)
    if request.user.get_profile().contacts.filter(user=user):
        return HttpResponse(_("Contact already added"))
    request.user.get_profile().contacts.add(user.get_profile())
    user.get_profile().get_default_observer().notify('invitation', sender=request.user)
    return HttpResponse(_("Invitation sent"), status=332)

def resetpassword(request):
    """sends an e-mail to the user with a new password"""
    try:
        user = User.objects.get(username=request.POST.get("username"))
    except User.DoesNotExist:
        return direct_to_template(request, template="users/resetpwd.html", extra_context = {'message': _("The user doesn't exist")})
    if user.email != request.POST["email"]:
        return direct_to_template(request, template="users/resetpwd.html", extra_context = {'message': _("E-mail address did not match")})
    password = User.objects.make_random_password()
    user.set_password(password)
    user.save()
    send_mail(_("New password"), _("Your password has been reset. Your new password is: %s")%password, "admin@open-initiative.com", [user.email])    
    return direct_to_template(request, template="users/resetpwd.html", extra_context = {'message': _("The new password has been sent to you by e-mail"),})

@login_required
def changepassword(request):
    """updates user's password"""
    if not request.user.check_password(request.POST["oldpassword"]):
        return HttpResponse(_("Old password did not match"))
    if request.POST['newpassword'] != request.POST['confirmpassword']:
        return HttpResponse('Passwords did not match')
    request.user.set_password(request.POST['newpassword'])
    request.user.save()
    messages.info(request, _("Your password has been updated"))
    return HttpResponseRedirect("/user/myaccount")

@login_required
def changeemail(request):
    """updates user's email address"""
    if request.POST['newemail'] != request.POST['confirmemail']:
        return HttpResponse('Addresses did not match')
    request.user.email = request.POST['newemail']
    request.user.save()
    messages.info(request, _("Your email has been updated"))
    return HttpResponseRedirect("/user/myaccount")

@login_required
def savebio(request):
    """updates user's bio"""
    request.user.get_profile().bio = request.POST['bio']
    request.user.get_profile().save()
    return HttpResponse(_("Modification saved"))

def createuser(request):
    """creates a new user"""
    if request.POST.get("acceptcgu") != "on":
        return direct_to_template(request, template="users/register.html", extra_context = {'message':_("Please accept the terms of use")})
    if not re.compile("^[\w\-\.]+$").search(request.POST.get("username")):
        return direct_to_template(request, template="users/register.html", extra_context = {'message':_("Invalid username. Please use only letters, digits, - and _.")})
    if not request.POST["password"]:
        return direct_to_template(request, template="users/register.html", extra_context = {'message':_("Please enter a password")})
    if request.POST["password"] != request.POST["password_confirm"]:
        return direct_to_template(request, template="users/register.html", extra_context = {'message':_("Passwords did not match")})
    try:
        user = User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password"])
    except IntegrityError:
        return direct_to_template(request, template="users/register.html", extra_context = {'message':_("This username is already used")})
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
    if not form.is_valid():
        messages.info(request, _("Incorrect data"))
        return HttpResponse('', status=332)
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
        return HttpResponse(_("Can not change other users' profiles"))
    detail.delete()
    return HttpResponse(_("Modification saved"))

@login_required
def settitle(request):
    """changes user's title"""
    request.user.get_profile().title = request.POST["title"]
    request.user.get_profile().save()
    return HttpResponse(_("Modification saved"))

@login_required
def settaxrate(request):
    """changes user's tax rate"""
    profile = request.user.get_profile()
    profile.tax_rate = request.POST["taxrate"]
    profile.save()
    return HttpResponse(_("Tax rate saved"))

@login_required
def listnamedisplays(request):
    """returns a list of user's possible name displays"""
    displays = map(lambda s:s%{'username':request.user.username, 'first':request.user.first_name, 'last':request.user.last_name}, OI_DISPLAYNAME_TYPES)
    return direct_to_template(request, template='users/profile/namedisplay.html', extra_context={'displays':displays})

@login_required
def setnamedisplay(request):
    """changes user full name display type"""
    if not request.POST.has_key("display"):
        return HttpResponse(_("Wrong arguments"), status=531)
    request.user.get_profile().display_name = request.POST["display"]
    request.user.get_profile().save()
    return HttpResponse(_("Modification saved"))

@login_required
def setbirthdate(request):
    """changes user's birth date"""
    request.user.get_profile().birthdate = request.POST["date"]
    request.user.get_profile().save()
    return HttpResponse(_("Modification saved"))

@login_required
def uploadpicture(request):
    """changes user's profile picture"""
    if request.user.get_profile().picture:
        request.user.get_profile().picture.delete()
    request.user.get_profile().picture.save("profile.jpg", File(request.FILES['picture']))
    return HttpResponse("<script>window.parent.document.getElementById('user_picture').src += '?%s'</script>"%(random())) #random to avoid cache issue

def getpicture(request, username):
    """Downloads given user's profile picture"""
    if not username or not get_object_or_404(User, username=username).get_profile().picture:
        return HttpResponseRedirect('/img/defaultusr.png') #default picture
    response = HttpResponse(mimetype='image/jpeg')
    response['X-Sendfile'] = "%suser/%s/profile.jpg"%(MEDIA_ROOT,username)
    try:
        response['Content-Length'] = os.path.getsize("%suser/%s/profile.jpg"%(MEDIA_ROOT,username))
    except OSError:
        raise Http404
    return response

@login_required
def invoice(request):
    """Exports the invoice of all user payments as pdf"""
    response = HttpResponse(render_to_pdf("users/pdf/invoice.html", {'user':request.user}), mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=invoice.pdf'
    return response

@login_required
def sendMP(request, username):
    """sends a private to the selected user, from the current user"""
    mp = PersonalMessage(from_user=request.user, to_user=User.objects.get(username = username), text=request.POST['message'], subject=request.POST['subject'])
    mp.save()
    mp.to_user.get_profile().get_default_observer().notify('personal_message', param=mp.subject, sender=mp.from_user)
    return HttpResponse(_("Message sent"), status=332)

@login_required
def archivenotice(request):
    """Sets the notice as archived, so that it doesn't appear in the user report anymore"""
    notice = Notice.objects.get(id=request.POST["notice"])
    if notice.recipient != request.user:
        raise Http404
    notice.archive()
    return HttpResponse(_("Notice archived"))

@login_required
def getusermessages(request, username):
    """gets all messages with the user"""
    contact = User.objects.get(username=username)
    to_messages = PersonalMessage.objects.filter(from_user=contact).filter(to_user=request.user)
    from_messages = PersonalMessage.objects.filter(to_user=contact).filter(from_user=request.user)
    messages = (to_messages|from_messages).order_by('sent_date')
    return direct_to_template(request, template="users/usermessages.html", extra_context = {'contact':contact,'personalmessages':messages})

@login_required
def confirmpayment(request):
    """asks user for confirmation before redirecting to payment service provider"""
    payment = Payment(user=request.user, amount=0, project_id=0, reason='Paiement en attente de validation')
    payment.save()
    amount = Decimal(request.POST['amount'].replace(',','.')).quantize(Decimal('.01'))
    params = {"PSPID":"openinitiative", "currency":"EUR", "language":"fr_FR", "TITLE":"", "BGCOLOR":"", "TXTCOLOR":"", "TBLBGCOLOR":"", "TBLTXTCOLOR":"", "BUTTONBGCOLOR":"", "BUTTONTXTCOLOR":"", "LOGO":"", "FONTTYPE":""}
    params['orderID'] = payment.id
    params['amount'] = (amount*100).quantize(Decimal('1.'))
    params["CN"] = "%s %s"%(request.user.first_name, request.user.last_name)
    params["EMAIL"] = request.user.email
    params["ownerZIP"] = request.user.get_profile().postcode
    params["owneraddress"] = request.user.get_profile().address
    params["ownercty"] = request.user.get_profile().country
    params["ownertown"] = request.user.get_profile().city
    params["ownertelno"] = request.user.get_profile().phone
    params["SHASign"] = computeSHA(params)
    return direct_to_template(request, template="users/confirmpayment.html",extra_context = {'params':params, 'amount':amount, 'action': PAYMENT_ACTION})
    
def updatepayment(request):
    """HTTP Server-to-server request from payment service provider sent after user payment"""
    import logging
    logging.getLogger("oi").debug(request)
    payment = Payment.objects.get(id=request.POST['orderID'])
    payment.user.get_profile().update_payment(dict(request.POST.items())) #to obtain a mutable version of the QueryDict
    return HttpResponse('OK') 
