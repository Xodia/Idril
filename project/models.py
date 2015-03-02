# -*- coding: utf8 -*-

'''
Voir le formset wizard pour faire la creation de projets en
plusieurs etapes.
1 - Nom du projet, contenu ;
2 - Gifts.

'''

from __future__ import unicode_literals
from django.db import models
from base.models import Media, Permission
# from member.models import Profile
from django.db import models
from django.forms import ModelForm
from datetime import date
from django.db.models import get_model # Erreur de double inclusion si import de payment.models -> Payment
from member.models import User
import datetime



class Gift(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    amount_required = models.DecimalField(max_digits=15, decimal_places=2)
    max_amount = models.IntegerField(null=True, default=None, blank=True)

    def __str__(self):
        return self.name

class ProjectCategory(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()

class Project(models.Model):
    STATECHOICE = (
        ('0', 'CANCELED'),
        ('1', 'IN PROGRESS'),
        ('2', 'FUNDED'),
        ('3', 'FAILED'),
        ('4', 'WAITING VALIDATION'),
    )
    user = models.ForeignKey(User) # Project's creator
    title = models.CharField(max_length=50, null=True)
    short_description = models.CharField(max_length=255, null=True)
    content = models.TextField(null=True)
    date = models.DateField(null=True, default=date.today())
    date_modified = models.DateField(null=True)
    end_date = models.DateField(null=True)
    amount_required = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    amount_actual = models.DecimalField(max_digits=15, decimal_places=2, null=True, default=0)
    state = models.CharField(max_length=1, choices=STATECHOICE, default=1, null=True)
    # medias = models.ManyToManyField(Media, null=True)
    header = models.FileField(upload_to="project/headers", null=True)
    permission = models.ForeignKey(Permission, null=True)
    category = models.ForeignKey(ProjectCategory, null=True)
    gifts = models.ManyToManyField(Gift, null=True, default=None, blank=True)

    def __str__(self):
        return self.title

    def get_funds_for_project(self):
        payment = get_model('payment', 'Payment')
        payment_list = payment.objects.all().filter(project__id=self.id, payment_status='PAID')
        amount = 0
        for payment in payment_list:
            amount += payment.price

        return amount

    def get_nb_gift_for_project(self, gift_id):
        payment = get_model('payment', 'Payment')
        count = payment.objects.all().filter(project__id=self.id,
                                                    payment_status='PAID',
                                                    gift__id=gift_id).count()
        if __debug__:
            print('--> Count for gift_id='+str(gift_id) + ': ' + str(count))
        return count

    def get_percentage(self):
        amount = self.get_funds_for_project()
        percent = (amount / self.amount_required) * 100
        percent = "%.1f" % percent
        return percent

    def get_days_left(self):
        _date = datetime.date.today()
        days = (self.end_date-_date).days
        return days

    def days_left(self):
        d1 = datetime.datetime.utcnow()
        d2 = self.end_date
        return abs((d2 - d1).days)

    def stop(self):
        self.state = '0'
        self.save()

    def is_in_progress(self):
        return self.state == '1'
    def is_cancelled(self):
        return self.state == '0'


class Funding(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=50, decimal_places=2)
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    gift = models.ForeignKey(Gift, null=True, default=None)

class ProjectComment(models.Model):
    content = models.TextField()
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    date = models.DateField(default=date.today())
