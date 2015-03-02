from django.shortcuts import render
from django.shortcuts import render_to_response
from models import Payment, PaypalInformations
from forms import PaymentForm, BankInformationsForm, PaypalInformationsForm
from django.template import RequestContext
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from project.models import Gift, Project
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import redirect
from django.contrib.messages import error
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from mangopay.client import get_mangopay_api_client
from mangopay_idril.models import IdrilMangoPayUser, IdrilMangoPayWallet
import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import sys

logger = logging.getLogger('idril')

@login_required
def index(request, project_id):
    # ciphertext = encrypt(password, 'my secret')
    # plaintext = decrypt(password, ciphertext)
    # 'test': plaintext,
    # 'testhash': hexlify(ciphertext)

    project = Project.objects.get(id=project_id)
    list_gifts = project.gifts.all()

    panier_amount = 0
    try:
        wallet = IdrilMangoPayWallet.get_personal_wallet(request.user.id)
        panier = wallet.balance()
        panier_amount = panier.amount
        print(panier.amount)

    except BaseException as e:
        print e

    if request.method == 'POST':
        post = request.POST
        print('POWST')
        print(post)
        # get gift_id -> if == 0 => No gift selected -> default
        # get 'gift_amount' -> Amount the user want to give

        print('iciiii>')
        if 'amount' in post and 'gift_choice' in post:
            try:
                if post.get('gift_choice') != 'none':
                    gift = Gift.objects.get(id=post.get('gift_choice'))
                    if gift and float(post.get('amount')) < float(gift.amount_required):
                        error = "Veuillez mettre un montant superieur a la valeur du cadeau"
                        print(error)
                        return render_to_response('payment/payment.html',
                                   {'project': project, 'list_gifts': list_gifts, 'error': error},
                                   context_instance=RequestContext(request))
                else:
                    gift = None

                if post.get('panier_choice') != 'none':
                    print('Transfer ? ')
                    print(float(post.get('amount')))
                    print('('+str(panier_amount)+') > ('+str(post.get('amount'))+')')
                    print('----->')
                    if panier_amount > float(post.get('amount')):
                        # transfer $$ to project
                        print('Transfert !!!!')
                        amount = float(post.get('amount'))
                        new_payment = Payment()
                        new_payment.create(None, request.user, amount, (amount * 0.018) + 0.18, gift, project)
                        new_payment.payment_status = 'PAID'
                        new_payment.save()
                        wallet_user = IdrilMangoPayWallet.get_personal_wallet(request.user.id)
                        #wallet_user.transfer_money_to_wallet(amount, project.id)

                        print('Success !')
                        send_mail('[IDRIL][Payment][#' + str(new_payment.id) + '] Paiement via CB ',
                        'Paiement via CB fait par ' + new_payment.bank_info.name_owner_card, 'morgan.collino@gmail.com',
                        ['morgan.collino@gmail.com'])
                        return render_to_response('payment/successfull.html',
                                      {'new_payment': new_payment},
                                      context_instance=RequestContext(request))

            except:
                raise Http404

            try:
                amount = post.get('amount')
                int_amount = float(amount)
            except:
                raise Http404 # Error Bad number

            print('-----0->')
            print(int_amount)
            print(amount)
            print('<-----0-')

            if int_amount <= 0 or amount == '':
                error = "Veuillez mettre un montant superieur a 0 euro"
                print(error)
                # Voir pour faire un fichier avec tout les erreurs en define
                render_to_response('payment/payment.html',
                                   {'project': project, 'list_gifts': list_gifts, 'error': error},
                                   context_instance=RequestContext(request))
            else:
                # Everything is OK
                payment = Payment()
                payment.price = int_amount
                payment.user_id = request.user
                payment.project_id = project.id
                if gift:
                    payment.gift_id = gift.id
                    return redirect('payment.views.payment_choice', project_id=project_id, gift_id=gift.id)
                return redirect('payment.views.payment_choice', project_id=project_id, gift_id=-1)

            #send_mail('[IDRIL][Payment][' + str(new_payment.id) + '] Paiement via CB ',
            #          'Paiement via CB fait par ' + new_payment.last_name, 'morgan.collino@gmail.com',
            #          ['morgan.collino@gmail.com'])
            #return render_to_response('payment/successfull.html',
            #                          {'new_payment': new_payment, 'hash_cb': decrypt('cypher_hash68210_xod', unhexlify(new_payment.card_number)).decode('utf8') },
            #                          context_instance=RequestContext(request))
            # print(messages.error(request, "Error"))

    return render_to_response('payment/payment.html',
                              {'project': project, 'list_gifts': list_gifts, 'panier':panier_amount},
                              context_instance=RequestContext(request))


def paypal(request):

    post = ""
    if request.method == 'POST':
            post = request.POST
    print(post)
    paypal_dict = {
        "business": "morgan.collino@gmail.com",
        "amount": "42.00",
        "item_name": "Don 42",
        "invoice": "unique-invoice-id",
        "notify_url": "http://ks3367383.kimsufi.com/paypal/"
                      "you/re/not/gonna/find/me/coeur/idril?transacID=42",
        # voir paiement ? Paypal senser pinger + info
        "return_url": "https://www.idril.fr/payment/paypal/return",
        "cancel_return": "https://www.idril.fr/payment//paypal/cancel",

        # mettre un ID dans l'url (GET) pour la confirmation
        # pour savoir QUEL paiement a cancel/confirmer ;)
        # WARNING: TOUJOURS TESTER EN PRODUCTION !
        # (Notify not working with local URL)

    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render_to_response('payment/paypal.html',
                              {'form': form},
                              context_instance=RequestContext(request))

''' Return paypal est appeler lors que le paiement via un utilisateur
 a ete validee et qu'il souhaite revenir sur la
    page d'Idril. Idril_payment > Paypal > Auth > Validation Payment
     > Success > Return to Idril '''


@csrf_exempt
def return_paypal(request, user_id, project_id, gift_id):

    ''' { POST RECUPERER PAR DR.PAYPAL }
         protection_eligibility, last_name, txn_id, receiver_email,
         payment_status payment_gross tax residence_countrymerchant_return_link
        invoice payer_status txn_type handling_amount payment_date,
        first_name item_name charset custom notify_version
        transaction_subject test_ipn item_number pending_reason
        payer_id auth verify_sign mc_currency shipping
        payer_email payment_type mc_gross quantity
    '''

    post = ""
    new_payment = None
    project = None
    user = None
    gift = None
    try:
        project = Project.objects.get(id=project_id)
        user = User.objects.get(id=user_id)
    except:
        raise BaseException
    try:
        gift = Gift.objects.get(id=gift_id)
    except Gift.DoesNotExist:
        gift = None

    post = ''
    if request.method == 'POST':
        post = request.POST
        paypal_info = PaypalInformations()
        paypal_info.first_name = request.POST.get('first_name', 0)
        paypal_info.last_name = request.POST.get('last_name', 0)
        paypal_info.item_name = request.POST.get('item_name', 0) + '-' + request.POST.get('mc_gross', 0) + 'euros'
        paypal_info.transaction_subject = request.POST.get('transaction_subject', 0)
        paypal_info.pending_reason = request.POST.get('pending_reason', 0)
        paypal_info.payer_id = request.POST.get('payer_id', 0)
        paypal_info.payer_email = request.POST.get('payer_email', 0)
        paypal_info.receiver_email = request.POST.get('receiver_email', 0)
        paypal_info.tracking_id = request.POST.get('txn_id', 0)
        paypal_info.save()

        new_payment = Payment()
        new_payment.user = user
        if gift:
            new_payment.gift = gift
        new_payment.project = project
        new_payment.paypal_info = paypal_info
        new_payment.tax = request.POST.get('tax', 0)
        new_payment.price = request.POST.get('mc_gross', 0)
        new_payment.payment_type = 'PAYPAL'
        #new_payment.payment_status = str(request.POST.get('payment_status', 0)).upper()
        new_payment.payment_status = 'PAID'
        new_payment.save()
        ''' PAYPAL RECORD '''

    print('RETURN_PAYPAL')
    print(post)
    print('!RETURN_PAYPAL')


    return render_to_response('payment/paypal/return.html',
                              {'post': post, 'new_payment': new_payment},
                              context_instance=RequestContext(request))


''' Cancel paypal est appeler lors que le paiement via un utilisateur
 a ete refuser/annuler et qu'il souhaite revenir sur la
    page d'Idril. Idril_payment > Paypal > Auth > Cancel > Return to Idril  '''


def cancel_paypal(request, user_id, project_id, gift_id):
    project = None
    user = None
    gift = None
    try:
        project = Project.objects.get(id=project_id)
        user = User.objects.get(id=user_id)
    except:
        raise BaseException
    try:
        gift = Gift.objects.get(id=gift_id)
    except Gift.DoesNotExist:
        gift = None

    new_payment = Payment()
    new_payment.user = user
    if gift:
        new_payment.gift = gift
    new_payment.project = project
    new_payment.price = 0
    new_payment.payment_type = 'PAYPAL'
    new_payment.payment_status = 'CANCEL'
    new_payment.save()
    ''' PAYPAL RECORD '''
    return render_to_response('payment/paypal/cancel.html', {},
                              context_instance=RequestContext(request))


# paypal/you/re/not/gonna/find/me/coeur/idril?transacID=42

'''A tester en prod : Lien non appeler en mode localhost !!!
 Notify = Notification URL appelee par Paypal lors de la
 validation/non-validation d'un paiement.Totalement diff
 de Cancel and Return URL. (Notify est appeler avant
 et l'user lambda ne la connait pas donc, c'est simple
 de glisser un ID pour referencer par exemple un paiement
 pour le valider en BDD. Dans ce cas: transacID.'''

'''
    Example d'une notification de Paypal (POST)
    To see log: /var/log/apache2/error.log

    NOTIFY_PAYPAL
    [Sun Mar 16 08:13:44 2014] [error]
    <QueryDict: {u'protection_eligibility':
    [u'Ineligible'], u'last_name': [u'testest'],
    u'txn_id': [u'4E511531YJ2785049'],
    u'receiver_email': [u'morgan.collino@gmail.com'],
    u'payment_status': [u'Pending'],u'payment_gross': [u'42.00'],
    u'tax': [u'0.00'], u'residence_country': [u'US'],
    u'invoice': [u'unique-invoice-id'],
    u'payer_status': [u'verified'],
    u'txn_type': [u'web_accept'],
    u'handling_amount': [u'0.00'],
    u'payment_date': [u'01:10:50 Mar 16, 2014 PDT'],
    u'first_name': [u'testest'], u'item_name': [u'Don 42'],
    u'charset': [u'windows-1252'], u'custom': [u''],
    u'notify_version': [u'3.7'], u'transaction_subject': [u''],
    u'test_ipn': [u'1'], u'item_number': [u''],
    u'pending_reason': [u'unilateral'],
    u'payer_id': [u'R4B47VGB6UK8S'],
    u'verify_sign':
    [u'AFcWxV21C7fd0v3bYYYRCpSSRl31AIZwDH3jdHQ51E3aVyBW9dn32n6a'],'
    u'mc_currency': [u'USD'],
    u'shipping': [u'0.00'],
    u'payer_email': [u'morgan.collino3@gmail.com'],
    u'payment_type': [u'instant'],
    u'mc_gross': [u'42.00'], u'ipn_track_id': [u'689ed2d7e423f'],
    u'quantity': [u'1']}>
    [Sun Mar 16 08:13:44 2014] [error]
    !NOTIFY_PAYPAL

    Relative informations : protection_eligibility, last_name,
    txn_id (transaction id, keep it to track), receiver_email,
    payment_status, payment_gross (amount paid), tax,
    residence_country, invoice (to set in Python-Django,
    could be giftID),payer_status, txn_type (Transaction type),
'''

@csrf_exempt
def notify_paypal(request, user_id, project_id, gift_id):

    project = None
    user = None
    gift = None
    try:
        project = Project.objects.get(id=project_id)
        user = User.objects.get(id=user_id)
    except:
        raise BaseException
    try:
        gift = Gift.objects.get(id=gift_id)
    except Gift.DoesNotExist:
        gift = None

    post = ''
    if request.method == 'POST':
        return
        post = request.POST
        paypal_info = PaypalInformations()
        paypal_info.first_name = request.POST.get('first_name', 0)
        paypal_info.last_name = request.POST.get('last_name', 0)
        paypal_info.item_name = request.POST.get('item_name', 0) + '-' + request.POST.get('mc_gross', 0) + 'euros'
        paypal_info.transaction_subject = request.POST.get('transaction_subject', 0)
        paypal_info.pending_reason = request.POST.get('pending_reason', 0)
        paypal_info.payer_id = request.POST.get('payer_id', 0)
        paypal_info.payer_email = request.POST.get('payer_email', 0)
        paypal_info.receiver_email = request.POST.get('receiver_email', 0)
        paypal_info.tracking_id = request.POST.get('txn_id', 0)
        paypal_info.save()

        new_payment = Payment()
        new_payment.user = user
        if gift:
            new_payment.gift = gift
        new_payment.project = project
        new_payment.paypal_info = paypal_info
        new_payment.tax = request.POST.get('tax', 0)
        new_payment.price = request.POST.get('mc_gross', 0)
        new_payment.payment_type = 'PAYPAL'
        new_payment.payment_status = str(request.POST.get('payment_status', 0)).upper()
        new_payment.save()
        ''' PAYPAL RECORD '''

    print('NOTIFY_PAYPAL')
    print(post)
    print('!NOTIFY_PAYPAL')

    return render_to_response('payment/paypal/notify.html',
                              context_instance=RequestContext(request))

@staff_member_required
def payment_list(request):

    order_by = ''
    s = ''
    entry_list = Payment.objects.order_by('-payment_date')
    if request.method == 'GET':
        get = request.GET
        print('GET:')
        print(get)
        print('----')
        if 's' in get:
            s = get.get('s')
            order = 'payment_date'
        if 'order_by' in get:
            order_by = get.get('order_by')
            if order_by == 'type':
                order = 'payment_type'
            if order_by == 'payment_asc':
                order = 'payment_date'
            if order_by == 'payment_desc':
                order = '-payment_date'
            if order_by == 'status':
                order = 'payment_status'
            print(order)
            entry_list = Payment.objects.filter(Q(bank_info__name_owner_card__icontains=s)
                                                | Q(paypal_info__last_name__icontains=s)
                                                | Q(user__username__icontains=s)
                                                | Q(paypal_info__first_name__icontains=s)
                                                | Q(project__title__icontains=s)).order_by(order)
        if 'project_id' in get:
            entry_list = entry_list.filter(Q(project__id=get.get('project_id')))

    paginator = Paginator(entry_list, 10)
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        entries = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        entries = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        post = request.POST
        if 'delete_paiement_id' in post:
            obj = Payment.objects.get(id=post['delete_paiement_id'])
            obj.delete()
            if 's' in post and 'order_by' in post:
                return HttpResponseRedirect("/payment/list?s=" + post.get('s') + '&order_by=' + post.get('order_by'))
            if 's' in post and not 'order_by' in post:
                return HttpResponseRedirect("/payment/list?s=" + post.get('s'))
            if not 's' in post and 'order_by' in post:
                return HttpResponseRedirect("/payment/list?order_by=" + post.get('order_by'))
            if not 's' in post and not 'order_by' in post:
                return HttpResponseRedirect("/payment/list")

    return render_to_response('payment/list.html', {'all_entries': entries,
                                                    'order_by': order_by,
                                                    's': s},
                              context_instance=RequestContext(request))

@staff_member_required
def payment_detail(request, payment_id="1"):

    try:
        obj = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        raise Http404

    # Decrypt le numero de carte de credit + cryptogramme
    # obj.card_number = decrypt(settings.PAYMENT_HASH, unhexlify(obj.card_number)).decode('utf8')
    # obj.cryptogram = decrypt(settings.PAYMENT_HASH, unhexlify(obj.cryptogram)).decode('utf8')

    form_payment = PaymentForm(instance=obj)
    print(obj.paypal_info)
    if obj.payment_type == 'CB':
        if obj.bank_info is None:
            form = BankInformationsForm()
        else:
            form = BankInformationsForm(instance=obj.bank_info)
    elif obj.payment_type == 'PAYPAL':
        if obj.paypal_info is None:
            form = PaypalInformationsForm()
        else:
            form = PaypalInformationsForm(instance=obj.paypal_info)

    if request.method == 'POST':
        post = request.POST
        print(post)
        if 'paiement' in post:
            form_payment = PaymentForm(post, instance=obj)
            if form_payment.is_valid():
                new_payment = form_payment.save(commit=False)
                new_payment.save()
                return HttpResponseRedirect("/payment/list")
            else:
                print('isNotValid! -. Paiement form')
                print(form_payment.errors)
        elif 'infos' in post:
            if obj.payment_type == 'CB':
                form = BankInformationsForm(post, instance=obj.bank_info)
                if form.is_valid():
                    obj.bank_info = form.save()
                    return HttpResponseRedirect("/payment/list")
                else:
                    print('isNotValid! -. InfosBank form')
            elif obj.payment_type == 'PAYPAL':
                form = PaypalInformationsForm(post, instance=obj.paypal_info)
                if form.is_valid():
                    obj.paypal_info = form.save()
                    return HttpResponseRedirect("/payment/list")
                else:
                    print('isNotValid! -. InfosPaypal form')
    return render_to_response('payment/detail.html', {'payment': obj, 'form': form,
                                                      'form_payment': form_payment},
                              context_instance=RequestContext(request))

@login_required
def payment_choice(request, project_id, gift_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404
    try:
        gift = Gift.objects.get(id=gift_id)
    except Gift.DoesNotExist:
        gift = None

    if gift:
        try:
            project_gift = Project.objects.filter(gifts__id=gift_id, id=project_id).count()
        except Gift.DoesNotExist:
            project_gift = None
        # print(project_gift)
        if project_gift == 0: # Means gift is not available in the project
            raise Http404
    user = request.user
    args = {}
    args.update(csrf(request))
    args['project'] = project

    amount = 0
    if request.method == 'POST':
        post = request.POST
        if 'gift_choice' in post:
            gift_choice = post.get('gift_choice')
            if gift_choice != 'none':
                try:
                    gift = Gift.objects.get(id=gift_choice)
                    amount = gift.amount_required
                except Gift.DoesNotExist:
                    gift = None
        print('gift:')
        print(gift)
        if 'amount' in post:
            err = ''
            try:
                amount = float(post.get('amount'))
            except:
                err = "Veuillez entrer un montant"
            if gift and float(post.get('amount')) < float(gift.amount_required):
                err = "Veuillez mettre un montant superieur a la valeur du cadeau"
            if  amount < 1:
                err = "Veuillez mettre un montant superieur ou egal a 1 euro"
            if err != '':
                error(request, err)
                return redirect('payment.views.index', project_id=project_id)

        args['amount'] = amount
        if gift:
            args['gift'] = gift
            args['description'] = gift.description
        else:
            args['description'] = 'No description'

        print('POST:')
        print(post)
    else:
        if gift:
            args['gift'] = gift
            args['description'] = gift.description
            amount = gift.amount_required
            args['amount'] = gift.amount_required
        else:
            args['description'] = ''
            args['amount'] = amount
            # En mode GET et t'as pas de GIFT -> Mode STFU ERROR

    args['amount'] = amount

    return render(request, 'payment/choice_payment.html', args)

import traceback


@login_required
def payment_cb(request, project_id, gift_id):

    # pour etre opti -> Recup id projet + id don + id user
    form = BankInformationsForm()
    amount_ht = 0
    amount_tax = 0
    amount_ttc = 0
    args = {}

    try:
        project = Project.objects.get(id=project_id)

    except Project.DoesNotExist:
        raise Http404
    try:
        gift = Gift.objects.get(id=gift_id)
        amount_ht = gift.amount_required
        amount_ttc = gift.amount_required
    except Gift.DoesNotExist:
        gift = None
    try:
        project_gift = Project.objects.filter(gifts__id=gift_id, id=project_id).count()
    except Project.DoesNotExist:
        if gift_id != -1: # Means gift is not available in the project
            raise Http404

    if request.method == 'POST':
        post = request.POST
        if 'gift_choice' in post:
            gift_choice = post.get('gift_choice')
            if gift_choice != 'none':
                try:
                    gift = Gift.objects.get(id=gift_choice)
                except Gift.DoesNotExist:
                    gift = None
        if post.get('panier_choice') != 'none':
                    print('Transfer ? ')
                    print(float(post.get('amount')))
                    wallet = IdrilMangoPayWallet.get_personal_wallet(request.user.id)
                    panier_amount = -1
                    try:
                        panier = wallet.balance()
                        panier_amount = panier.amount
                        print('('+str(panier_amount)+') > ('+str(post.get('amount'))+')')
                        print('----->')
                    except BaseException as e:
                        print(e)
                    if panier_amount > float(post.get('amount')):
                        # transfer $$ to project
                        print('Transfert !!!!')
                        amount = float(post.get('amount'))
                        new_payment = Payment()
                        new_payment.create(None, request.user, amount, (amount * 0.018) + 0.18, gift, project)
                        new_payment.payment_status = 'PAID'
                        new_payment
                        new_payment.save()
                        wallet_user = IdrilMangoPayWallet.get_personal_wallet(request.user.id)
                        wallet_user.transfer_money_to_wallet(amount, project.id)

                        print('Success !')

                        return render_to_response('payment/successfull.html',
                                      {'new_payment': new_payment},
                                      context_instance=RequestContext(request))

    card_list = []
    try:
        mangopay_user = IdrilMangoPayUser.objects.get(user__id=request.user.id)
        cards = get_mangopay_api_client().users.GetCards(mangopay_user.mangopay_id)
        for card in cards:
            cardd = get_mangopay_api_client().cards.Get(card.Id)
            #if cardd.Validity == "VALID":
            card_list.append(cardd)

    except BaseException as e:
        print traceback.format_exc()
        print(e)

    if project_gift == 0 and gift_id != '-1':
        raise Http404

    if request.method == 'POST':
        post = request.POST
        print(post)
        if 'y' not in post:
            if 'amount' in post:
                amount_ht = float(post.get('amount'))
                amount_ttc = float(post.get('amount'))
            form = BankInformationsForm(post)
            if form.is_valid():
                new_payment = Payment()
                new_payment.create(form, request.user, amount_ht, (amount_ht * 0.018) + 0.18, gift, project)
                new_payment.payment_status = 'PAID'
                new_payment.save()
                try:
                    mangopay_user = IdrilMangoPayUser.objects.get(user__id=request.user.id)
                   # card_registration = mangopay_user.save_card(new_payment)
                    mangopay_user.make_payment(new_payment, project, amount_ttc, amount_tax)
                except BaseException as e:
                    print('Exception: Payment MangoPayUser error')
                    print (e)
                    print (e.message)
                    print traceback.print_exc()

                print('Success !')
                send_mail('[IDRIL][Payment][#' + str(new_payment.id) + '] Paiement via CB ',
                      'Paiement via CB fait par ' + new_payment.bank_info.name_owner_card, 'morgan.collino@gmail.com',
                      ['morgan.collino@gmail.com'])
                return redirect("successfull", payment=new_payment.id)

                #return render_to_response('payment/successfull.html',
                 #                     {'new_payment': new_payment},
                  #                    context_instance=RequestContext(request))
            else:
                print('isNotValid!')
                print(form.errors)
        else:
            if 'amount' in post:
                amount = post.get('amount')
                amount_ht = 1
                try:
                    amount_ht = float(amount)
                except Exception:
                    amount_ht = 1
                amount_tax = (amount_ht * 0.018) + 0.18
                amount_ttc = amount_ht # amount_ht + amount_tax

    args.update(csrf(request))
    args['form'] = form
    args['project'] = project
    args['gift'] = gift
    args['amount_ttc'] = amount_ttc
    args['amount_ht'] = amount_ht
    args['amount_tax'] = amount_tax
    args['cards'] = card_list

    return render(request, 'payment/new.html', args)

@login_required
def payment_list_user(request):

    order_by = ''
    s = ''
    user = request.user
    entry_list = Payment.objects.all().filter(Q(user__id__contains=user.id)).order_by('payment_date')
    if request.method == 'GET':
        get = request.GET
        print('GET:')
        print(get)
        print('----')
        if 's' in get:
            s = get.get('s')
            order = 'payment_date'
            if 'order_by' in get:
                order_by = get.get('order_by')
                if order_by == 'payment_asc':
                    order = 'payment_date'
                if order_by == 'payment_desc':
                    order = '-payment_date'
            print(order)
            entry_list = Payment.objects.filter(Q(paypal_info__first_name__icontains=s)
                                                | Q(paypal_info__last_name__icontains=s)
                                                | Q(paypal_info__last_name__icontains=s)
                                                | Q(bank_info__name_owner_card__icontains=s)
                                                | Q(user__username__icontains=s)
                                                | Q(project__title__icontains=s),
                                             user__id__exact=user.id).order_by(order)

    return render_to_response('payment/list_user.html', {'all_entries': entry_list,
                                                    'order_by': order_by,
                                                    's': s},
                              context_instance=RequestContext(request))

def response(request):
    if request.method == 'GET':
        get = request.GET
        print('GET:')
        print(get)
    if request.method == 'POST':
        post = request.POST
        print('POST:')
        print(post)
    return render_to_response('payment/nothing_to_be_done_here.html',
                                      context_instance=RequestContext(request))

@login_required
def my_payments(request):
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
    return render(request, 'payment/paymentinformations.html', args)

@login_required
def refund(request, user_id, payment_id):
    args = {}
    try:
        wallet_user = IdrilMangoPayWallet.get_personal_wallet(user_id)
        res = wallet_user.refund_payment(payment_id)
        args['success'] = res
    except BaseException as e:
        print('Error refunds : refund() -> payment.views.')
        print(e.message)
        print(e)
        print traceback.format_exc()

    args.update(csrf(request))
    return render(request, 'payment/refund.html', args)

@login_required
def successfull(request, payment=None):
    new_payment = 0
    if payment:
        new_payment = Payment.objects.all().get(id=payment)
    return render(request, 'payment/successfull.html', {'new_payment':new_payment})
