from django.contrib import admin
from mangopay_idril.models import MangoPayNaturalUser, MangoPayWallet
from mangopay_idril.models import IdrilMangoPayUser, IdrilMangoPayWallet, IdrilMangoPayTransfer

admin.site.register(MangoPayNaturalUser)
admin.site.register(IdrilMangoPayUser)
admin.site.register(IdrilMangoPayWallet)
admin.site.register(MangoPayWallet)
admin.site.register(IdrilMangoPayTransfer)