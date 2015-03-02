# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django import forms
from models import Profile
from models import Address
from models import MailMessage
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from tinymce.widgets import TinyMCE
from django.conf import settings

class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'txt'})
        self.fields['new_password1'].widget.attrs.update({'class': 'txt'})
        self.fields['new_password2'].widget.attrs.update({'class': 'txt'})

class UserChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['first_name'].widget.attrs.update({'class': 'txt'})
        self.fields['last_name'].widget.attrs.update({'class': 'txt'})
        self.fields['email'].widget.attrs.update({'class': 'txt'})

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class ProfileChangeForm(forms.ModelForm):
    birth_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    def __init__(self, *args, **kwargs):
        super(ProfileChangeForm, self).__init__(*args, **kwargs)
        self.fields['birth_date'].widget.attrs.update({'class': 'txt'})
        self.fields['description'].widget.attrs.update({'class': 'txt'})
        self.fields['avatar'] = forms.ImageField(label=('Avatar'),required=False, error_messages = {'invalid': ("Image files only")}, widget=forms.FileInput)
        self.fields['avatar'].widget.attrs.update({'class': 'button-avatar'})
        GENDER = (
            ('0', 'Homme'),
            ('1', 'Femme'),
        )
        self.fields['gender'] = forms.ChoiceField(choices=GENDER,
                                                  widget=forms.RadioSelect(attrs={'style': '-webkit-appearance: radio; list-style:none;'}))

    class Meta:
        model = Profile
        fields = ('birth_date', 'gender', 'avatar', 'description',)

    def save(self, commit=True):
        profile = super(ProfileChangeForm, self).save(commit=False)
        if commit:
            profile.save()
        return profile


class UserAddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserAddressForm, self).__init__(*args, **kwargs)
        self.fields['street1'].widget.attrs.update({'class': 'txt'})
        self.fields['street2'].widget.attrs.update({'class': 'txt'})
        self.fields['zip_code'].widget.attrs.update({'class': 'txt'})
        self.fields['city'].widget.attrs.update({'class': 'txt'})
        self.fields['phone_number1'].widget.attrs.update({'class': 'txt'})
        self.fields['phone_number2'].widget.attrs.update({'class': 'txt'})

    class Meta:
        model = Address
        fields = ('street1', 'street2', 'zip_code', 'city', 'phone_number1',
                  'phone_number2',)

    def save(self, commit=True):
        address = super(UserAddressForm, self).save(commit=False)
        if commit:
            address.save()
        return address


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = True
        self.fields['username'].widget.attrs.update({'class': 'txt'})
        self.fields['password1'].widget.attrs.update({'class': 'txt'})
        self.fields['password2'].widget.attrs.update({'class': 'txt'})
        self.fields['first_name'].widget.attrs.update({'class': 'txt'})
        self.fields['last_name'].widget.attrs.update({'class': 'txt'})
        self.fields['email'].widget.attrs.update({'class': 'txt'})
        self.fields['username'].widget.attrs['placeholder'] = "NOM D'UTILISATEUR"
        self.fields['email'].widget.attrs['placeholder'] = "ADRESSE E-MAIL"
        self.fields['password1'].widget.attrs['placeholder'] = "MOT DE PASSE"
        self.fields['password2'].widget.attrs['placeholder'] = "MOT DE PASSE VÉRIFICATION"
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name',)

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        # user.is_active = False # A decommenter pour utiliser
        # la confirmation par e-mail
        if commit:
            user.save()
        return user

class NewMessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewMessageForm, self).__init__(*args, **kwargs)
        self.fields['receiver'].widget.attrs.update({'class': ''})
        self.fields['content'].required = True
        self.fields['content'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = MailMessage
        fields = ('receiver', 'content')

    def save(self, commit=True):
        message = super(NewMessageForm, self).save(commit=False)
        if commit:
            message.save()
        return message