# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django import forms
from django.forms import ModelForm
from project.models import Project
from project.models import Gift
from project.models import ProjectComment
from django.utils.translation import gettext as _
from django.forms.models import modelformset_factory
from tinymce.widgets import TinyMCE
from django.conf import settings

import time
import datetime

class ProjectFormEdit(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectFormEdit, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'class': 'txt'})
        self.fields['header'] = forms.ImageField(label=('Image d\'en tête'),required=False, error_messages = {'invalid': ("Image files only")}, widget=forms.FileInput)
        self.fields['header'].widget.attrs.update({'id': 'inputProjectImg'})
        self.fields['short_description'].widget.attrs.update({'class': 'txt'})

    class Meta:
        model = Project
        fields = ('content', 'header', 'short_description',)
        labels = {
            'content': _('Contenu'),
            'header': _('En-tête'),
            'short_description' :_('Description courte'),
        }

#class DateInput(forms.DateInput):
#    input_type = 'date'

#class MyModelForm(ModelForm):
#    class Meta:
#        model = MyModel
#        fields = '__all__'
#        widgets = {
#            'my_date': DateInput()
#        }

class ProjectFormCreate(ModelForm):
    end_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    def __init__(self, *args, **kwargs):
        super(ProjectFormCreate, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'txt'})
        self.fields['short_description'].widget.attrs.update({'class': 'txt'})
        self.fields['content'].widget.attrs.update({'class': 'txt'})
        self.fields['amount_required'].widget.attrs.update({'class': 'txt', 'step': '1', 'min': '1'})
        self.fields['end_date'].widget.attrs.update({'class': 'txt'})
        self.fields['header'] = forms.ImageField(label=('Image d\en tête'),required=False, error_messages = {'invalid': ("Image files only")}, widget=forms.FileInput)
        self.fields['header'].widget.attrs.update({'id': 'inputProjectImg'})
    class Meta:
        model = Project
        fields = ('title', 'short_description', 'content', 'amount_required', 'category', 'end_date', 'header',)
        labels = {
            'title': _('Titre'),
            'short_description': _('Description courte'),
            'content': _('Contenu'),
            'amount_required': _('Montant requis'),
            'category': _('Categorie'),
            'end_date': _('Date de fin de financement'),
            'header': _('En-tête'),
        }

    def clean_end_date(self):
        data = self.cleaned_data['end_date']
        notTooFarTime = None
        notBeforeTime = None
        dateTimeProjectEnd = datetime.datetime.fromtimestamp(time.mktime(time.strptime(str(data), "%Y-%m-%d")))
        try:
            notTooFarTime = dateTimeProjectEnd < datetime.datetime.now() + datetime.timedelta(90,0)
            notBeforeTime = dateTimeProjectEnd > datetime.datetime.now() + datetime.timedelta(7,0)
        except Exception:
            raise forms.ValidationError("Le format de la date de fin du projet n'est pas valide.")
        if notTooFarTime == False:
            raise forms.ValidationError("Un projet doit avoir une durée maximale de 90 jours.")
        if notBeforeTime == False:
            raise forms.ValidationError("Un projet doit avoir une durée minimale de 7 jours.")
        return data

class GiftFormCreate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GiftFormCreate, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'txt'})
        self.fields['description'].widget.attrs.update({'class': 'txt', 'style': 'width:100%;'})
        self.fields['amount_required'].widget.attrs.update({'class': 'txt', 'step': 1, 'min': 1})
        self.fields['max_amount'].widget.attrs.update({'class': 'txt', 'step': 1, 'min': 1})
        
    class Meta:
        model = Gift
        fields = ('name', 'description', 'amount_required', 'max_amount',)
        labels = {
            'name': _('Nom'),
            'description': _('Description'),
            'amount_required': _('Montant requis'),
            'max_amount': _('Nombre max. dispo.'),
        }

GiftFormSetCreate = modelformset_factory(Gift, form=GiftFormCreate)

class AddCommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddCommentForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'class': 'txt', 'style': 'width:90%;'})

    class Meta:
        model = ProjectComment
        fields = ('content',)
