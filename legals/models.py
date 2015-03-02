# -*- coding: utf8 -*-

'''
Voir le formset wizard pour faire la creation de projets en
plusieurs etapes.
1 - Nom du projet, contenu ;
2 - Gifts.

'''

from __future__ import unicode_literals
from member.models import User
from project.models import Project
from django.db import models

class Legal(models.Model):
    STATECHOICE = (
        ('0', 'REFUSED'),
        ('1', 'IN PROGRESS'),
        ('2', 'VALIDATED'),
    )

    RISKCHOICE = (
        ('0', 'ALL CLEAR'),
        ('1', 'DOUBT'),
        ('2', 'SUSPICIOUS'),
        ('3', 'CODE RED')
    )
    #user = models.ForeignKey(User) # Project's creator
    project = models.ForeignKey(Project)
    date = models.DateField(auto_now=True)
    date_modified = models.DateField(auto_now=True)
    state = models.CharField(max_length=1, choices=STATECHOICE, default=1, null=True)
    risk = models.CharField(max_length=1, choices=RISKCHOICE, default=1, null=True)
    last_reviewer = models.ForeignKey(User) # Validator / Updator
    identification_manager = models.FileField(upload_to="project/legals", null=True)
    identification_association = models.FileField(upload_to="project/legals", null=True)
    #legal_ = models.FileField(upload_to="project/legals", null=True)

    def __str__(self):
        return self.title