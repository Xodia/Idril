# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django.db import models
from member.models import User
from datetime import datetime
from base.models import Permission
from django.utils.timezone import utc
from django.contrib import admin

class Category(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()

    def __unicode__(self):
        return self.title

class Topic(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(User)  # FK
    date = models.DateTimeField(null=True, default=datetime.utcnow().replace(tzinfo=utc))
    date_modified = models.DateField(null=True)

class Message(models.Model):
    content = models.TextField()
    date = models.DateTimeField(null=True, default=datetime.utcnow().replace(tzinfo=utc))
    date_modified = models.DateTimeField(null=True)
    author = models.ForeignKey(User)  # FK
    topic = models.ForeignKey(Topic)  # FK

    def __unicode__(self):
        return self.content

Message.likes = property(lambda u: Like.objects.filter(message=u, state='1').count() - Like.objects.filter(message=u, state='0').count())

class Like(models.Model):
    CHOICE = (
        ('0', 'DISLIKE'),
        ('1', 'LIKE'),
    )
    user = models.ForeignKey(User)  # FK
    message = models.ForeignKey(Message)  # FK
    state = models.CharField(max_length=1, choices=CHOICE, default=1, null=True)
    date = models.DateTimeField(null=True, default=datetime.utcnow().replace(tzinfo=utc))

admin.site.register(Topic)
admin.site.register(Message)
