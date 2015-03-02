from __future__ import unicode_literals
from django import forms
from django.forms import ModelForm
from mangopay_idril.models import IdrilMangoPayUser, IdrilMangoPayWallet

class IdrilMangoPayUserForm(ModelForm):
    class Meta:
        model = IdrilMangoPayUser
        exclude = ('',)
        # fields = '__all__'

class IdrilMangoPayWalletForm(ModelForm):
    class Meta:
        model = IdrilMangoPayWallet
        exclude = ('',)
        # fields = '__all__'