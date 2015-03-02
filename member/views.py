# -*- coding: utf8 -*-

from __future__ import unicode_literals
import datetime
import hashlib
import uuid

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import auth
from django.conf import settings
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.core.context_processors import csrf
from django.contrib.sites.models import get_current_site
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.timezone import utc

from member.models import Profile
from models import User
from project.models import Project
from member.models import MailMessage
from member.forms import UserChangeForm
from member.forms import ProfileChangeForm
from member.forms import RegistrationForm
from member.forms import UserPasswordChangeForm
from member.forms import UserAddressForm
from member.forms import NewMessageForm

from payment.models import Payment
from mangopay_idril.models import IdrilMangoPayUser, IdrilMangoPayWallet
from mangopay.client import get_mangopay_api_client
from django.db.models import Q

def get_random_string(string_length=10):
    random = str(uuid.uuid4())  # Convert uuid format to python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the uuid '-'.
    return random[0:string_length]


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/member/')
    args = {}
    return render(request, 'member/login.html', args)


@login_required
def member(request):
    args = {}
        # args['user'] = request.user
        # args['new_messages'] = MailMessage.objects.filter(receiver=request.user, read=False).count()
        # args.update(csrf(request))
    return profile(request)


def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    args = {}
    args.update(csrf(request))
    if user is not None:    
        auth.login(request, user)
        profile = None
        try:
            profile = Profile.objects.get(user__id=user.id)
        except Exception as E:
            profile = Profile
            profile.user = user

        try:
            mangopay_userwallet = IdrilMangoPayWallet.get_personal_wallet(request.user.id)
            usermangopay = IdrilMangoPayUser.objects.get(user__id=request.user.id)
        except Exception as e:
            print("Stop here !")
            print(e.message)
            profile.create_mangopay()

        if user.is_active is False:
            args = {}
            args.update(csrf(request))
            args['error'] = True
            args['error_message'] = "Identifiants incorrects"
            return render(request, 'member/login.html', args)
        return HttpResponseRedirect('/member/')
    else:
        args = {}
        args['error'] = True
        args['error_message'] = "Vos identifiants sont incorrects"
        args.update(csrf(request))
        return render(request, 'member/login.html', args)


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/member/login')

def profile_view(request, username):
    user = User.objects.get(username=username)

    args = {}
    args['user'] = user
    args.update(csrf(request))
    return render(request, 'member/profile_view.html', args)

@login_required
def profile(request):
    args = {}
    MessageForm = NewMessageForm()
    try:
        wallet = IdrilMangoPayWallet.get_personal_wallet(request.user.id)
        panier = wallet.balance()
        args['Panier'] = panier.amount
        print('Panier: ' + str(panier))
    except BaseException:
        print('No wallet - Connected to the current User :' + str(request.user.id))

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect('/member/')
        UserForm = UserChangeForm(request.POST, instance=request.user)
        ProfileForm = ProfileChangeForm(request.POST, request.FILES,
                                        instance=request.user.profile)
        AddressForm = UserAddressForm(request.POST,
                                      instance=request.user.address)
        if UserForm.is_valid() and ProfileForm.is_valid() and AddressForm.is_valid():
            print("valid");
            user = UserForm.save()
            profile = ProfileForm.save()
            address = AddressForm.save(commit=False)
            address.user = user
            address.save()
            args['success'] = True
            args['success_message'] = "Votre profil a été correctement\
                                        enregistré."
        else:
            print(UserForm.errors);
            print(ProfileForm.errors);
            print(AddressForm.errors);
    else:
        user = request.user
        UserForm = UserChangeForm(instance=user)
        ProfileForm = ProfileChangeForm(instance=user.profile)
        AddressForm = UserAddressForm(instance=request.user.address)
        MessageForm = NewMessageForm()
    messages = MailMessage.objects.filter(receiver=request.user)
    projects = Project.objects.filter(user=request.user)
    payins = []
    cards = []
    try:
        mangopay_user = IdrilMangoPayUser.objects.filter(user__id=request.user.id)[:1]
        if mangopay_user:
            cards = get_mangopay_api_client().users.GetCards(mangopay_user[0].mangopay_id)
        if mangopay_user:
            payins = Payment.objects.all().filter(Q(user__id__contains=request.user.id)).order_by('-payment_date')
    except Exception as e:
        print(e.message)
    # args['projects'] = projects
    args['Messages'] = messages
    args['UserForm'] = UserForm
    args['ProfileForm'] = ProfileForm
    args['AddressForm'] = AddressForm
    args['NewMessageForm'] = MessageForm
    args['Projects'] = projects
    args['Cards'] = cards
    args['Payins'] = payins
    args.update(csrf(request))
    return render(request, 'member/member.html', args)


@login_required
def password_change(request):
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect('/member/')
        PasswordForm = UserPasswordChangeForm(user=request.user,
                                              data=request.POST)
        if PasswordForm.is_valid():
            PasswordForm.save()
            args = {}
            args['user'] = request.user
            args['PasswordForm'] = PasswordForm
            args['success'] = True
            args['success_message'] = "Votre mot de passe\
                                       a été correctement modifié."
            args.update(csrf(request))
            return render(request, 'member/password_change.html', args)
    else:
        PasswordForm = UserPasswordChangeForm(user=request.user)
    args = {}
    args.update(csrf(request))
    args['PasswordForm'] = PasswordForm
    return render(request, 'member/password_change.html', args)


def send_mail_confirmation(request, user, activation_key):
    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain
    c = {
         'user': user,
         'domain': domain,
         'site_name': site_name,
         'protocol': 'http',
         # 'protocol': 'https' if use_https else 'http',
         'activation_key': activation_key,
        }
    subject = 'Confirmez votre compte'
    email = loader.render_to_string("member/register_confirm_email.html", c)
    send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email])


def set_activation_key(profile):
    # Creation activation key
    salt = hashlib.new("sha1")
    salt.update(get_random_string())
    activation_key = hashlib.new("sha1")
    activation_key.update(salt.hexdigest()+profile.user.username)
    # Set to profile
    profile.activation_key = activation_key.hexdigest()
    profile.key_expires = datetime.datetime.now() + datetime.timedelta(hours=6)

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/member/')
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect('/member/')
        UserForm = RegistrationForm(request.POST)
        ProfileForm = ProfileChangeForm()
        AddressForm = UserAddressForm()
        if UserForm.is_valid():
            user = UserForm.save()
            profile = ProfileForm.save(commit=False)
            profile.user = user
            set_activation_key(profile)
            profile.save()

            profile.create_mangopay()

            address = AddressForm.save(commit=False)
            address.user = user
            address.save()

            # send_mail_confirmation
            send_mail_confirmation(request, user, profile.activation_key)
            args = {}
            args['success'] = True
            args['success_message'] = "Félicitations vous êtes\
                                       maintenant inscrit ! Veuillez vous rendre sur votre boite mail pour valider votre inscription."
            args.update(csrf(request))
            return render(request, 'member/login.html', args)
        else:
            print UserForm.errors
    else:
        UserForm = RegistrationForm()
    args = {}
    args['UserForm'] = UserForm
    args.update(csrf(request))
    return render(request, 'member/register.html', args)


def register_confirm(request, activation_key):
    args = {}
    profile = get_object_or_404(Profile, activation_key=activation_key)
    if profile is not None:
        if profile.key_expires > datetime.datetime.utcnow().replace(tzinfo=utc) and profile.supression_date is None:
            profile.user.is_active = True
            profile.activation_key = None
            profile.key_expires = None
            profile.user.save()
            profile.save()
            args['success'] = True
            args['success_message'] = "Votre compte est désormais activé."
            return render(request, 'member/register_confirm.html', args)
    args['error'] = True
    args['error_message'] = "Ce lien d'activation a expiré ou n'existe pas."
    return render(request, 'member/register_confirm.html', args)


@login_required
def delete_account(request):
    user = request.user
    auth.logout(request)
    user.is_active = False
    profile = user.profile
    profile.supression_date = datetime.datetime.utcnow()
    profile.save()
    user.save()
    args = {}
    args['success'] = True
    args['success_message'] = "Votre compte a été correctement supprimé."
    args.update(csrf(request))
    return render(request, 'member/login.html', args)

# MAILBOX

@login_required
def all_messages(request):
    messages = MailMessage.objects.filter(receiver=request.user)
    args = {}
    args['active'] = 'inbox'
    args['messages'] = messages
    args.update(csrf(request))
    return render(request, 'member/messages.html', args)

@login_required
def inbox_messages(request):
    messages = MailMessage.objects.filter(receiver=request.user)
    args = {}
    args['active'] = 'inbox'
    args['messages'] = messages
    args.update(csrf(request))
    return render(request, 'member/messages.html', args)

@login_required
def inbox_unread_messages(request):
    messages = MailMessage.objects.filter(receiver=request.user, read=False)
    args = {}
    args['active'] = 'unread'
    args['messages'] = messages
    args.update(csrf(request))
    return render(request, 'member/messages.html', args)

@login_required
def sent_messages(request):
    messages = MailMessage.objects.filter(sender=request.user)
    args = {}
    args['active'] = 'sent'
    args['messages'] = messages
    args.update(csrf(request))
    return render(request, 'member/messages.html', args)

@login_required
def new_message(request):
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect('/member/') 

        mPost = request.POST # Mutable Copy (Override form.receiver)
        if 'id_receiver' in request.POST:
            mPost = request.POST.copy()
            to = User.objects.get(username=request.POST['id_receiver'])
            mPost['receiver'] = to.id
        messageForm = NewMessageForm(mPost)

        if messageForm.is_valid():
            message = messageForm.save(commit=False)
            message.sender = request.user
            message.save()
            return HttpResponseRedirect('/member/profile')
    else:
        messageForm = NewMessageForm()
    args = {}
    if request.method == 'GET':
        if 'to' in request.GET:
            args['to'] = request.GET.get('to')
    args.update(csrf(request))
    args['newMessageForm'] = messageForm
    return render(request, 'member/new_message.html', args)

@login_required
def markread(request):
    if request.method == 'POST':
        messageId = request.POST['messageId']
        response = MailMessage.objects.filter(id=messageId).update(read=True)
        if response == 1:
            return HttpResponse("OK");
        else:
            return HttpResponse("KO");
    else:
        return HttpResponse("KO");

@login_required
def delete(request):
    if request.method == 'POST':
        messageId = request.POST['messageId']
        response = MailMessage.objects.filter(id=messageId).delete()
        return HttpResponse("OK");
    else:
        return HttpResponse("KO");

@login_required
def payments(request):
    user = request.user
    payins = []
    cards = []
    try:
        mangopay_user = IdrilMangoPayUser.objects.get(user__id=user.id)
        if mangopay_user:
            cards = get_mangopay_api_client().users.GetCards(mangopay_user.mangopay_id)
        if mangopay_user:
            payins = Payment.objects.all().filter(Q(user__id__contains=user.id)).order_by('payment_date')
    except Exception:
        print(Exception.message)

    args = {}
    args.update(csrf(request))
    args['cards'] = cards
    args['payins'] = payins
    return render(request, 'member/payments.html', args)
