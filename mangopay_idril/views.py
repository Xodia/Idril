from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from mangopay_idril.models import MangoPayNaturalUser, MangoPayWallet
from django.contrib import admin
from mangopay_idril.models import IdrilMangoPayUser, IdrilMangoPayWallet
from project.models import Project
from mangopay_idril.forms import IdrilMangoPayUserForm, IdrilMangoPayWalletForm
from mangopay.client import get_mangopay_api_client
from payment.models import Payment
from django.db.models import Q
admin.autodiscover()

@staff_member_required
def list(request):

    users = IdrilMangoPayUser.objects.all()
    wallets = IdrilMangoPayWallet.objects.exclude(project__isnull=True)
    return render_to_response('mangopay/list.html', {'all_entries': users, 'wallets': wallets},
                              context_instance=RequestContext(request))

@staff_member_required
def wallets(request):

    wallets = IdrilMangoPayWallet.objects.all()
    return render_to_response('mangopay/wallets.html', {'all_entries': wallets},
                              context_instance=RequestContext(request))

@staff_member_required
def wallet(request, project_id):

    # project = Project.objects.get(id=project_id)
    try:
        walletz = IdrilMangoPayWallet.objects.get(project__id=project_id)
        wallet_mango = walletz._get()

        payments = Payment.objects.all().filter(Q(project__id__contains=walletz.project.id))
        #Payment.objects.values('user__id').annotate(the_count=Count('myCharField'))
    except BaseException as e:
        print(e)

    return render_to_response('mangopay/wallet.html', {'wallet': walletz, 'wallet_mango': wallet_mango,
                                                       'nb_dons': payments.count()
                                                       },
                              context_instance=RequestContext(request))

@staff_member_required
def wallet_personal(request, user_id):

    walletz = IdrilMangoPayWallet.get_personal_wallet(user_id)
    wallet_mango = walletz._get()
    return render_to_response('mangopay/wallet.html', {'wallet': walletz, 'wallet_mango': wallet_mango                                                    },
                              context_instance=RequestContext(request))


@staff_member_required
def refunds(request, project_id):

    project = 0
    wallet = IdrilMangoPayWallet.objects.get(project__id=project_id)
    wallet_mango = wallet._get()
    payments = Payment.objects.all().filter(Q(project__id__contains=wallet.project.id))

    success = 0

    return render_to_response('mangopay/refunds.html', {'project': project, 'wallet' : wallet,
                                                        'wallet_mp': wallet_mango, 'success': success})

@staff_member_required
def refunds_userpayment(request, user_id, payment_id):

    return

@staff_member_required
def users(request):
    client = get_mangopay_api_client()
    users = client.users.GetAll()
    all_entries = []
    for user in users:
        res = client.users.Get(user.Id)
        all_entries.append(res)
    return render_to_response('mangopay/users.html', {'all_entries': all_entries},
                              context_instance=RequestContext(request))