from __future__ import absolute_import
from django.contrib import admin
from payment.models import Payment, PaypalInformations, BankInformations
from mangopay_idril.models import MangoPayNaturalUser, MangoPayWallet
from mangopay_idril.models import IdrilMangoPayWallet, IdrilMangoPayUser

admin.site.register(Payment)
admin.site.register(PaypalInformations)
admin.site.register(BankInformations)
