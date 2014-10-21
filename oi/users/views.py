#coding: utf-8
# Vues des utilisateurs
import os, re
from random import random
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import URLValidator
from django.db.models import get_app, Count, Avg
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse, Http404, QueryDict
from django.shortcuts import render_to_response, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.simplejson import JSONEncoder, JSONDecoder
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.i18n import set_language
from oi.prjnotify.models import Notice, NoticeType, Observer
from oi.helpers import render_to_pdf, OI_DISPLAYNAME_TYPES, computeSHA
from oi.messages.templatetags.oifilters import oiescape
from oi.users.models import User, UserProfile, UserProfileForm, PersonalMessage, Payment
from oi.users.models import Training, TrainingForm, Experience, ExperienceForm, Skill, SkillForm, OI_USERPROFILE_DETAILS_CLASSES
from oi.projects.models import Bid, Project
from oi.settings_common import MEDIA_ROOT

@login_required
def myprofile(request):
    """shows the profile of the current user"""
    extra_context = {'selected_user':request.user}
    extra_context.update(Bid.objects.filter(project__assignee=request.user).aggregate(Count("rating"),Avg("rating")))
    return TemplateResponse(request, "users/profile/profile.html", extra_context)

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
    return TemplateResponse(request, "users/profile/profile.html", extra_context)

@login_required
def myaccount(request):
    """user settings page or asks user for confirmation before redirecting to payment service provider"""
    import logging
    logging.getLogger("oi").debug("user returned: %s"%request)
    extra_context = {}
    params = {}
    if request.GET.get("orderID"): #return from payment
        
        dict_params = dict(request.GET.items()) #to obtain a mutable version of the QueryDict
        if dict_params.get("project"): 
            project = Project.objects.get(id=dict_params.pop("project"))
            params = {"PARAMPLUS": project}

            #delta is the amount actually added, considering this function can be called several times
            #the second time, delta is probably 0
            delta = request.user.profile.update_payment(dict_params)
            if delta:
                project.makebid(request.user, delta) #to update the user account
        else:
            request.user.profile.update_payment(dict_params) 
        
        extra_context['params'] = params
        return TemplateResponse(request, 'users/myaccount.html', extra_context)
        
    elif request.GET.get("amount"): #request for payment
        amount = Decimal((request.GET['amount']).replace(',','.')).quantize(Decimal('.01'))
        if request.GET.get("project"): #from a bid
            extra_context['task'] = Project.objects.get(id=request.GET["project"])
            amount = amount - request.user.profile.balance #only pay what the user lacks
            
        if request.GET.get("deposit"): #from account page
            amount += Decimal((request.GET['deposit']).replace(',','.')).quantize(Decimal('.01'))
            
        payment = Payment(user=request.user, amount=0, project_id=None, reason='Paiement en attente de validation')
        payment.save()
        
        params = {"PSPID":"openinitiative", "currency":"EUR", "TITLE":"", "BGCOLOR":"", "TXTCOLOR":"", "TBLBGCOLOR":"", "TBLTXTCOLOR":"", "BUTTONBGCOLOR":"", "BUTTONTXTCOLOR":"", "LOGO":"", "FONTTYPE":""}
        params['orderID'] = payment.id
        params['amount'] = (amount*100).quantize(Decimal('1.'))
        params["CN"] = "%s %s"%(request.user.first_name, request.user.last_name)
        params["EMAIL"] = request.user.email
        params["ownerZIP"] = request.user.profile.postcode
        params["owneraddress"] = request.user.profile.address
        params["ownercty"] = request.user.profile.country
        params["ownertown"] = request.user.profile.city
        params["ownertelno"] = request.user.profile.phone
        params["language"] = "%s_%s"%(request.LANGUAGE_CODE,request.LANGUAGE_CODE)
        if request.GET.get("project"):
            params["PARAMPLUS"] = "project=%s"%request.GET["project"]
        params["SHASign"] = computeSHA(params)
        extra_context['params'] = params 
        extra_context['action'] = settings.PAYMENT_ACTION
        extra_context['amount'] = amount
        
    extra_context['contact_form'] = UserProfileForm(instance=request.user.profile)    
    return TemplateResponse(request, 'users/myaccount.html', extra_context)

@login_required
def setemailing(request):
    """sets email sending for a given notice type for the current user"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        notice_type = NoticeType.objects.get(label=request_dict["label"])
        send = (request_dict["send"] == "true")
        setting = Observer.objects.get(request.user).get_setting.update(send=send)
        return HttpResponse(_("Setting saved"))

@login_required
def savename(request):
    """saves user contact information"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        request.user.last_name = request_dict['lastname']
        request.user.first_name = request_dict['firstname']
        request.user.save()
        return HttpResponse(_("Name saved"))

@login_required
def savecontactinfo(request):
    """saves user contact information"""
    
    request_dict = QueryDict(request.body)
    form = UserProfileForm(request_dict, instance=request.user.profile)
    if request.method == "POST":
        if request_dict.get("personal_website"):
            validate = URLValidator(request_dict.get("personal_website"))
            try:
                URLValidator(request_dict.get("personal_website"))
            except ValidationError, e:
                return HttpResponse(_("Thank you to enter a valid url address"))
        if form.is_valid():
            form.save() 
            return HttpResponse(_("Information saved"))
        return HttpResponse(_("The form is not valid"))

@login_required
def setrss(request):
    """saves rss feed url into user's profile"""
    profile = request.user.profile
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        profile.rss_feed = request_dict["rss"]
        profile.save()
        return HttpResponse("Feed url saved")

@login_required
def invite(request, username):
    """adds a user as a contact of the current user"""
    user = User.objects.get(username = username)
    if request.user.profile.contacts.filter(user=user):
        return HttpResponse(_("Contact already added"))
    request.user.profile.contacts.add(user.profile)
    user.profile.get_default_observer().notify('invitation', sender=request.user)
    return HttpResponse(_("Invitation sent"), status=332)

def resetpassword(request):
    """sends an e-mail to the user with a new password"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        try:
                user = User.objects.get(username=request_dict.get("username"))
        except User.DoesNotExist:
            extra_context = {'message': _("The user doesn't exist")}
            return TemplateResponse(request, "users/resetpwd.html", extra_context)
            if user.email != request_dict["email"]:
                extra_context = {'message': _("E-mail address did not match")}
                return TemplateResponse(request, "users/resetpwd.html", extra_context)
        password = User.objects.make_random_password()
        user.set_password(password)
        user.save()
        send_mail(_("New password"), _("Your password has been reset. Your new password is: %s")%password, "admin@open-initiative.com", [user.email]) 
        extra_context = {'message': _("The new password has been sent to you by e-mail"),}   
        return TemplateResponse(request, "users/resetpwd.html", extra_context)

@login_required
def changepassword(request):
    """updates user's password"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        if not request.user.check_password(request_dict["oldpassword"]):
            return HttpResponse(_("Old password did not match"))
        if request_dict['newpassword'] != request_dict['confirmpassword']:
            return HttpResponse('Passwords did not match')
        request.user.set_password(request_dict['newpassword'])
        request.user.save()
        messages.info(request, _("Your password has been updated"))
        return HttpResponseRedirect("/user/myaccount")

@login_required
def changeemail(request):
    """updates user's email address"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        if request_dict['newemail'] != request_dict['confirmemail']:
            return HttpResponse('Addresses did not match')
        request.user.email = request_dict['newemail']
        request.user.save()
        messages.info(request, _("Your email has been updated"))
        return HttpResponseRedirect("/user/myaccount")
    
def changeuserlanguage(request):
    """change user language"""
    user = request.user
    lang = request.POST.get("language")

    if user.is_authenticated():
        user.profile.language = lang
        user.profile.save()
    
    #change the website language    
    return set_language(request) 

@login_required
def savebio(request):
    """updates user's bio"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        request.user.profile.bio = request_dict['bio']
        request.user.profile.save()
        return HttpResponse(_("Modification saved"))

def createuser(request):
    """creates a new user"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        if request_dict.get("acceptcgu") != "on":
            extra_context = {'message':_("Please accept the terms of use")}
            return TemplateResponse(request, "users/register.html", extra_context)
        if not re.compile("^[\w\-\.]+$").search(request_dict.get("username")):
            extra_context = {'message':_("Invalid username. Please use only letters, digits, - and _.")}
            return TemplateResponse(request, "users/register.html", extra_context)
        if not request_dict["password"]:
            extra_context = {'message':_("Please enter a password")}
            return TemplateResponse(request, "users/register.html", extra_context)
        if request_dict["password"] != request_dict["password_confirm"]:
            extra_context = {'message':_("Passwords did not match")}
            return TemplateResponse(request, "users/register.html", extra_context)
        try:
            user = User.objects.create_user(request_dict["username"], request_dict["email"], request_dict["password"])
        except IntegrityError:
            extra_context = {'message':_("This username is already used")}
            return TemplateResponse(request, "users/register.html", extra_context)
        user.first_name = request_dict["firstname"]
        user.last_name = request_dict["lastname"]
        user.save()
        return HttpResponseRedirect(reverse('oi.users.views.myprofile'))

@login_required
def editdetail(request, id):
    """edit resume detail of the user"""
    request_dict = QueryDict(request.body)
    if request.method == "GET":
        type = request_dict["type"]
        #gets the classes corresponding to the detail type
        objclass,formclass = OI_USERPROFILE_DETAILS_CLASSES[type]    
        if id=='0': #new detail
            instance = objclass(user=request.user)
        else:
            instance = objclass.objects.get(id=id)

        divid = request_dict.get("divid")
        form = formclass(instance=instance, prefix=divid) #prefix form elements with divid to allow multiple edition at the same time
        return render_to_response("users/profile/editdetail.html",{'user':request.user,'id':id,'form':form,'divid':divid,'type':type})

@login_required
def savedetail(request, id):
    """saves a resume detail of the user"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        type = request_dict["type"]
        #gets the classes corresponding to the detail type
        objclass,formclass = OI_USERPROFILE_DETAILS_CLASSES[type]
        if id=='0': #new detail
            instance = objclass(user=request.user)
        else:
            instance = objclass.objects.get(id=id)
        form = formclass(request_dict, instance=instance, prefix=request_dict['divid'])
        if not form.is_valid():
            messages.info(request, _("Incorrect data"))
            return HttpResponse('', status=332)
        instance = form.save()
        return render_to_response("users/profile/%s.html"%type,{'user':request.user, type:instance, 'selected_user':request.user})
    
@login_required
def deletedetail(request, id):
    """deletes a detail from the user's resume"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        type = request_dict["type"]
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
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        request.user.profile.title = request_dict["title"]
        request.user.profile.save()
        return HttpResponse(_("Modification saved"))

@login_required
def settaxrate(request):
    """changes user's tax rate"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        profile = request.user.profile
        profile.tax_rate = request_dict["taxrate"]
        profile.save()
        return HttpResponse(_("Tax rate saved"))

@login_required
def listnamedisplays(request):
    """returns a list of user's possible name displays"""
    displays = map(lambda s:s%{'username':request.user.username, 'first':request.user.first_name, 'last':request.user.last_name}, OI_DISPLAYNAME_TYPES)
    extra_context={'displays':displays}
    return TemplateResponse(request, 'users/profile/namedisplay.html', extra_context)

@login_required
def setnamedisplay(request):
    """changes user full name display type"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        if not request_dict.has_key("display"):
            return HttpResponse(_("Wrong arguments"), status=531)
        request.user.profile.display_name = request_dict["display"]
        request.user.profile.save()
        return HttpResponse(_("Modification saved"))

@login_required
def setbirthdate(request):
    """changes user's birth date"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        request.user.profile.birthdate = request_dict["date"]
        request.user.profile.save()
        return HttpResponse(_("Modification saved"))

@login_required
def uploadpicture(request):
    """changes user's profile picture"""
    if request.user.profile.picture:
        request.user.profile.picture.delete()
    request.user.profile.picture.save("profile.jpg", File(request.FILES['picture']))
    return HttpResponse("<script>window.parent.document.getElementById('user_picture').src += '?%s'</script>"%(random())) #random to avoid cache issue

def getpicture(request, username):
    """Downloads given user's profile picture"""
    if not username or not get_object_or_404(User, username=username).profile.picture:
        return HttpResponseRedirect('/img/defaultusr.png') #default picture
    response = HttpResponse(mimetype='image/jpeg')
    response['X-Sendfile'] = "%suser/%s/profile.jpg"%(settings.MEDIA_ROOT,username)
    try:
        response['Content-Length'] = os.path.getsize("%suser/%s/profile.jpg"%(settings.MEDIA_ROOT,username))
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
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        mp = PersonalMessage(from_user=request.user, to_user=User.objects.get(username = username), text=oiescape(request_dict['message']), subject=request_dict['subject'])
        mp.save()
        mp.to_user.profile.get_default_observer().notify('personal_message', param=mp.subject, sender=mp.from_user)
        return HttpResponse(_("Message sent"), status=332)

@login_required
def archivenotice(request):
    """Sets the notice as archived, so that it doesn't appear in the user report anymore"""
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        notice = Notice.objects.get(id=request_dict["notice"])
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
    extra_context = {'contact':contact,'personalmessages':messages}
    return TemplateResponse(request, "users/usermessages.html", extra_context)

@csrf_exempt
def updatepayment(request):
    """HTTP Server-to-server request from payment service provider sent after user payment"""
    import logging
    logging.getLogger("oi").debug(request)
    
    request_dict = QueryDict(request.body)
    if request.method == "POST":
        dict_params = dict(request_dict.items()) #to obtain a mutable version of the QueryDict
        user = Payment.objects.get(id=request_dict['orderID']).user
        if dict_params.get("project"): 
            project = Project.objects.get(id=dict_params.pop("project"))
            delta = user.profile.update_payment(dict_params)
            if delta:
                project.makebid(user, delta)
        else:
            user.profile.update_payment(dict_params)
        return HttpResponse('OK')
