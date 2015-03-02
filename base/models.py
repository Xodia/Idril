# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django.db import models
from member.models import User

class Media(models.Model):
    name = models.CharField(max_length=30)
    url = models.CharField(max_length=200)
    date = models.DateField()
    #File = models.FileField(blank=True, null=True)

class Achievement(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField()
    media = models.ForeignKey(Media, null=True) #FK

class News(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    date = models.DateField()
    date_modified = models.DateField(null=True)
    media = models.ManyToManyField(Media, null=True) #MTM
    user = models.ForeignKey(User) #FK

class Permission(models.Model):
    name = models.CharField(max_length=30)
    def __unicode__(self):
        return self.name