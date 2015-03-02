from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from project.models import Gift, Project
from simplecrypt import encrypt, decrypt
from binascii import hexlify, unhexlify
from django.conf import settings
TITLE_CHOICES = (
    ('MR', 'Mr.'),
    ('MRS', 'Mrs.'),
    ('MS', 'Ms.'),
)

CARD_CHOICES = (
    ('VISA', 'Visa'),
    ('MASTERCARD', 'MasterCard'),
    ('CB', 'Carte bleue'),
    ('AMERICANEXPRESS', 'American Express')
)

COUNTRY_CHOICES = (
    ('FRANCE', 'France'),
    ('SUISSE', 'Suisse'),
    ('LUXEMBOURG', 'Luxembourg'),
    ('BELGIQUE', 'Belgique'),
    ('USA', 'Etats-Unis')
)

MONTH_EXP_CHOICES = (
    ('01', 1),
    ('02', 2),
    ('03', 3),
    ('04', 4),
    ('05', 5),
    ('06', 6),
    ('07', 7),
    ('08', 8),
    ('09', 9),
    ('10', 10),
    ('11', 11),
    ('12', 12)
)

TYPE_CHOICES = (
    ('PAYPAL', 'Paypal'),
    ('CB', 'Carte bleue'),
    ('MANGOPAY', 'MangoPay')
)
YEARS_EXP_CHOICES = (
    ('2015', 2015),
    ('2016', 2016),
    ('2017', 2017),
    ('2018', 2018),
    ('2019', 2019),
    ('2020', 2020)
)

STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('CANCELED', 'Canceled'),
    ('DENIED', 'Denied'),
    ('FAILED', 'Failed'),
    ('PAID', 'Paid'),
)

class PaypalInformations(models.Model):
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    item_name = models.CharField(max_length=100, null=True)
    transaction_subject = models.CharField(max_length=100, null=True)
    pending_reason = models.CharField(max_length=100, null=True)
    payer_id = models.CharField(max_length=100, default='NO_PAYPAL_ID')
    payer_email = models.CharField(max_length=100, null=True)
    receiver_email = models.CharField(max_length=100, null=True)
    payment_date = models.DateTimeField(max_length=100, auto_now=True, null=False)
    tracking_id = models.CharField(max_length=100, default='0')

    def __init__(self, *args, **kwargs):
        super(PaypalInformations, self).__init__(*args, **kwargs)

    def __str__(self):
        return 'Paypal informations: ' + str(self.id)

class BankInformations(models.Model):
    name_owner_card = models.CharField(max_length=120, null=False)
    address = models.CharField(max_length=100, null=False)
    address2 = models.CharField(max_length=100, null=True)
    expiration_month = models.CharField(max_length=2,
                                        choices=MONTH_EXP_CHOICES, null=False)
    expiration_year = models.CharField(max_length=4,
                                      choices=YEARS_EXP_CHOICES, null=False)
    cryptogram = models.CharField(max_length=142, null=False)
    card_type = models.CharField(max_length=40,
                                choices=CARD_CHOICES, null=True)
    zip_code = models.CharField(max_length=5, null=False)
    card_number = models.CharField(max_length=200, null=False)
    country = models.CharField(max_length=30,
                               choices=COUNTRY_CHOICES, null=False)
    city = models.CharField(max_length=200, null=False)

    def __init__(self, *args, **kwargs):
        super(BankInformations, self).__init__(*args, **kwargs)

    def __str__(self):
        return 'Bank informations: ' + str(self.id)

    def _card_number(self):
        res = decrypt(settings.PAYMENT_HASH, unhexlify(self.card_number)).decode('utf8')
        return res
    def _cvx(self):
        res = decrypt(settings.PAYMENT_HASH, unhexlify(self.cryptogram)).decode('utf8')
        return res
    def _expiration_data_mmaa(self):
        month = str(self.expiration_month)
        year = str(self.expiration_year)
        year = year[-2:]
        res = month + '' + year # should give MMAA e.g [1] [2014] and give 0114
        return res

class Payment(models.Model):
    user = models.ForeignKey(User)
    gift = models.ForeignKey(Gift, null=True)
    project = models.ForeignKey(Project)
    paypal_info = models.ForeignKey(PaypalInformations, null=True)
    bank_info = models.ForeignKey(BankInformations, null=True)
    price = models.DecimalField(max_digits=42, decimal_places=2, max_length=9, default='0')
    tax = models.DecimalField(max_digits=42, decimal_places=2, max_length=9, default='0')
    payment_date = models.DateTimeField(max_length=100, auto_now=True, null=False)
    payment_status = models.CharField(max_length=100, default='Pending', choices=STATUS_CHOICES)
    payment_type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    payment_date.editable=True
    refunded = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Payment, self).__init__(*args, **kwargs)

    def get_fields(self):
        return [(field.name, field.value_to_string(self))
                for field in Payment._meta.fields]
    def create(self, form, user, price_ht, tax, gift, project):
        self.payment_type = 'CB'
        self.payment_status = 'PAID'
        self.user = user
        self.tax = tax
        self.price = price_ht
        self.gift = gift
        self.project = project
        if form != None:
            bank_info = form.save()
            self.bank_info = bank_info
    def set_has_been_refunded(self, res):
        self.refunded = res
        self.save()

    def has_been_refunded(self):
        return self.refunded

    def __unicode__(self):
        return 'Payment ' + str(self.id) + ' for project ' + str(self.project_id)

    def __str__(self):
        return 'Payment ' + str(self.id) + ' for project ' + str(self.project_id)