# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib.admin.views.decorators import staff_member_required 
from django.shortcuts import render_to_response
from django.template import RequestContext
from member.forms import UserChangeForm
from member.forms import ProfileChangeForm
from member.forms import UserAddressForm
from mangopay_idril.models import IdrilMangoPayWallet
from django.db.models import Q
from models import User

@staff_member_required
def member_list(request):
    order_by = ''
    s = ''
    entry_list = list(User.objects.order_by('date_joined'))
    if request.method == 'GET':
        get = request.GET
        print('GET:')
        print(get)
        print('----')
        if 's' in get:
            s = get.get('s')
            order = 'date_joined'
            if 'order_by' in get:
                order_by = get.get('order_by')
                if order_by == 'last_name':
                    order = 'last_name'
                if order_by == 'first_name':
                    order = 'first_name'
                if order_by == 'status':
                    order = 'is_active'                    


            entry_list = User.objects.filter(Q(last_name__icontains=s) | Q(first_name__icontains=s) | Q(username__icontains=s)).order_by(order)

    # if request.method == 'POST':
    #     post = request.POST
    #     print('POST:')
    #     print(post)
    #     print('----')
    #     if 'delete_paiement_id' in post:
    #         obj = Payment.objects.get(id=post['delete_paiement_id'])
    #         obj.delete()
    #         if 's' in post and 'order_by' in post:
    #             return HttpResponseRedirect("/payment/list?s=" + post.get('s') + '&order_by=' + post.get('order_by'))
    #         if 's' in post and not 'order_by' in post:
    #             return HttpResponseRedirect("/payment/list?s=" + post.get('s'))
    #         if not 's' in post and 'order_by' in post:
    #             return HttpResponseRedirect("/payment/list?order_by=" + post.get('order_by'))
    #         if not 's' in post and not 'order_by' in post:
    #             return HttpResponseRedirect("/payment/list")

    return render_to_response('administration/member_list.html', {'all_entries': entry_list, 'order_by': order_by, 's': s}, context_instance=RequestContext(request))

@staff_member_required
def edit_member(request, username):
    args = {}
    user = User.objects.get(username=username)
    has_wallet = IdrilMangoPayWallet.has_personal_wallet(user.id)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect('/administration/member/')
        UserForm = UserChangeForm(request.POST, instance=user)
        ProfileForm = ProfileChangeForm(request.POST, request.FILES,
                                        instance=user.profile)
        AddressForm = UserAddressForm(request.POST,
                                      instance=user.address)
        if UserForm.is_valid() and ProfileForm.is_valid() and AddressForm.is_valid():
            user = UserForm.save()
            profile = ProfileForm.save()
            address = AddressForm.save(commit=False)
            address.user = user
            address.save()
            args['success'] = True
            args['success_message'] = "Le profil a été correctement\
                                        enregistré."
    else:
        user = user
        UserForm = UserChangeForm(instance=user)
        ProfileForm = ProfileChangeForm(instance=user.profile)
        AddressForm = UserAddressForm(instance=user.address)
    args['UserForm'] = UserForm
    args['ProfileForm'] = ProfileForm
    args['AddressForm'] = AddressForm
    args['Has_Wallet'] = has_wallet
    args.update(csrf(request))
    return render(request, 'administration/member_edit.html', args)

