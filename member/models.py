# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.utils.timezone import utc
from django.contrib.auth.models import User
from django.contrib import admin
from mangopay_idril.models import IdrilMangoPayUser, IdrilMangoPayWallet

class Profile(models.Model):
    GENDER = (
        ('0', 'MALE'),
        ('1', 'FEMALE'),
    )
    user = models.OneToOneField(User)
    birth_date = models.DateField(null=True)
    gender = models.CharField(max_length=1, choices=GENDER, default=0,
                              null=True)
    description = models.TextField(null=True)
    supression_date = models.DateField(null=True)
    activation_key = models.CharField(max_length=40, null=True)
    key_expires = models.DateTimeField(null=True)
    avatar = models.FileField(upload_to="avatar/",
                              default='default-avatar.jpeg')  # FK
    gifts = models.ManyToManyField('project.Gift')  # MTM
    achievements = models.ManyToManyField('base.Achievement')  # MTM

    def __unicode__(self):
        return unicode(self.user)

    def create_mangopay(self):
        try:
            mangopay_user = IdrilMangoPayUser.objects.get(user__id=self.user.id)
        except Exception:
            mangopay_user = IdrilMangoPayUser()
            print('USER:')
            print(self.user)
            mangopay_user.create_user(self.user, 'FR', 'FR', self.birth_date)
        try:
            userwallet = IdrilMangoPayWallet.objects.get(user__id=self.user.id)
        except Exception:
            userwallet = IdrilMangoPayWallet()
            userwallet.create_userwallet(mangopay_user, self.user)

User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])
User.address = property(lambda u: Address.objects.get_or_create(user=u)[0])


class Address(models.Model):
    street1 = models.CharField(max_length=100)
    street2 = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=50)
    phone_number1 = models.CharField(max_length=20)
    phone_number2 = models.CharField(max_length=20, blank=True)
    user = models.ForeignKey(User)  # FK


class PersonnalInformation(models.Model):
    credit_card_number = models.CharField(max_length=20)
    credit_card_expiration_date = models.DateField()
    user = models.ForeignKey(User)  # FK


class MailMessage(models.Model):
    receiver = models.ForeignKey(User, related_name='mailMessage_receiver')  # FK
    sender = models.ForeignKey(User, related_name='mailMessage_sender')  # FK
    date = models.DateTimeField(null=True, default=datetime.utcnow().replace(tzinfo=utc))
    subject = models.CharField(max_length=50)
    content = models.TextField()    
    read = models.BooleanField(default=False)

admin.site.register(Profile)
admin.site.register(Address)
