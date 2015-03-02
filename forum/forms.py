# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django import forms
from django.forms import ModelForm
from forum.models import Topic
from forum.models import Message
from tinymce.widgets import TinyMCE


class TopicFormCreate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TopicFormCreate, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'field'})

    class Meta:
        model = Topic
        fields = ('title',)
        labels = {
            'title': ('Titre'),
        }


class MessageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['content'].required = True
        self.fields['content'].widget.attrs.update({'class': 'txt'})

    class Meta:
        model = Message
        fields = ('content',)
        labels = {
            'content': ('Contenu'),
        }
