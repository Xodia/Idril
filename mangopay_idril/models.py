from __future__ import unicode_literals
from mangopay.models import MangoPayNaturalUser, MangoPayWallet, MangoPayPayIn, MangoPayCardRegistration
from django.db import models
from member.models import User
from project.models import Project
from mangopay.client import get_mangopay_api_client
from money import CURRENCY
from mangopaysdk.types.exceptions.responseexception import ResponseException
import requests
from payment.models import Payment
from django.conf import settings
from mangopaysdk.entities.transfer import Transfer
from money import Money as PythonMoney
from decimal import Decimal, ROUND_FLOOR
from mangopaysdk.types.money import Money

from django.utils.timezone import utc
from money.contrib.django.models.fields import MoneyField

from datetime import datetime

TRANSACTION_STATUS_CHOICES = (
    ('CREATED', "The request is created but not processed."),
    ('SUCCEEDED', "The request has been successfully processed."),
    ('FAILED', "The request has failed."),
)

PROJECT_TYPE_CHOICES = (
    ('PERSONAL', "The wallet is linked to a given user."),
    ('PROJECT', "The wallet is linked to a project."),
)

def python_money_to_mangopay_money(python_money):
    amount = python_money.amount.quantize(Decimal('.01'),
                                          rounding=ROUND_FLOOR) * 100
    return Money(amount=int(amount), currency=str(python_money.currency))

class IdrilMangoPayWallet(MangoPayWallet):
    # Regular Authenication Fields:
    user = models.ForeignKey(User) # Wallet's creator
    project = models.ForeignKey(Project, null=True)
    type = models.CharField(max_length=9, choices=PROJECT_TYPE_CHOICES, null=False)

    def __unicode__(self):
        return 'Wallet: ' + str(self.mangopay_id)

    @staticmethod
    def has_personal_wallet(user_id):
        projects = IdrilMangoPayWallet.objects.all().filter(user__id=user_id).filter(type='PERSONAL')[:1]
        if projects.count() == 0:
            return False
        return True


    @staticmethod
    def get_personal_wallet(user_id):
        projects = IdrilMangoPayWallet.objects.all().filter(user__id=user_id).filter(type='PERSONAL')[:1]
        if projects.count() == 0:
            # auto created one
            mangouser = IdrilMangoPayUser.objects.get(user__id=user_id)
            return IdrilMangoPayWallet.create_userwallet(mangouser, mangouser.user)
        return projects[0]

    @staticmethod
    def get_project_wallet(project_id):
        projects = IdrilMangoPayWallet.objects.all().filter(project__id=project_id).filter(type='PROJECT')[:1]
        if projects.count() == 0:
            return None
        return projects[0]

    def create_wallet(self, user, project):
        list = []
        for x in user.projects.all():
            list.append(x)
        user.projects = list
        user.save()
        self.mangopay_user = user
        self.user = project.user
        self.project = project
        self.type = 'PROJECT'
        self.save()
        try:
            self.create("EUR", project.title + "'s wallet")
        except BaseException as e:
            print(e)

        return self

    def create_userwallet(self, mangouser, user):
        self.mangopay_user = mangouser
        self.user = user
        self.type = 'PERSONAL'
        self.save()
        try:
            self.create("EUR", user.username +"'s wallet")
        except BaseException as e:
            print(e)
        return self

    def refund_payment(self, payment_id):
        res = True
        try:
            payment = Payment.objects.get(id=payment_id)
            print(payment_id)
            if payment.has_been_refunded():
                res = False

            if res is not False:
                user = IdrilMangoPayUser.objects.all().get(user__id=payment.user.id)
                project = payment.project

                print(payment.project)
                print(payment.project.id)
                project_wallet = IdrilMangoPayWallet.get_project_wallet(project.id)
                print(project_wallet)

                transfert = IdrilMangoPayTransfer()
                transfert.mangopay_id = user.mangopay_id
                transfert.mangopay_debited_wallet = project_wallet
                transfert.mangopay_credited_wallet = self
                transfert.debited_funds = PythonMoney(payment.price, "EUR")

                transfert.create()
                payment.set_has_been_refunded(True)
                res = True
        except Exception as e:
            print('Payment can not be refund - Does not exist')
            print(e)
            res = False
        print('RES : ---->')
        print(res)
        return res

    def transfer_money_to_wallet(self, amount, project_id):
        try:
            to = IdrilMangoPayWallet.get_project_wallet(project_id)
            if to == None:
                print('Project does not have wallet referenced to it !')
                return False
            user = IdrilMangoPayUser.objects.all().get(user__id=self.user.id)

            transfer = IdrilMangoPayTransfer()
            transfer.mangopay_id = user.mangopay_id
            transfer.mangopay_debited_wallet = self
            transfer.mangopay_credited_wallet = to
            transfer.debited_funds = PythonMoney(amount, "EUR")
            transfer.create()
            res = True

        except Exception as e:
            print('Transfer failed')
            print(e)
            res = False
        return res

import sys, traceback

class IdrilMangoPayUser(MangoPayNaturalUser):
    projects = models.ManyToManyField(Project, null=True)

    def __unicode__(self):
        return str(self.mangopay_id)

    def get_mangopay_wallet(self):
        return IdrilMangoPayWallet.get_personal_wallet(self.id)

    def create_user(self, user, nationality, country_of_residence, birth_date):
        self.user = user
        self.user.last_name = 'Unknown'
        self.user.first_name = 'Unknown'
        self.country_of_residence = country_of_residence
        self.nationality = nationality
        self.birthday = datetime.now()
        try:
            self.save()
            self.create()
        except Exception as e:
            print('EXCEPTION')
            print(e)
            traceback.print_exc(file=sys.stdout)

        return self

    def save_card(self, payment):
        card_registration = MangoPayCardRegistration()
        card_registration.mangopay_user = self
        card_registration.create("EUR")
        data = card_registration.get_preregistration_data()
        if settings.DEBUG:
            print('DATA----->')
            print(data)
            print(data.get('cardRegistrationURL'))
            print('END----->')

        client = get_mangopay_api_client()
        registration = client.cardRegistrations.Get(card_registration.mangopay_id)
        data = 'data=' + registration.PreregistrationData + '&accessKeyRef=' + registration.AccessKey;
        data += '&cardNumber='+str(payment.bank_info._card_number())+'&cardExpirationDate='+str(payment.bank_info._expiration_data_mmaa()) +'&cardCvx='+ str(payment.bank_info._cvx())
        headers = {"Content-Type" : "application/x-www-form-urlencoded", 'Connection':'close'}
        response = requests.post(registration.CardRegistrationURL, data, verify=False, headers=headers)

        if response.status_code != requests.codes.ok:
            raise ResponseException(response.request.url, response.status_code, response.text)
        res = response.text
        card_registration_m = client.cardRegistrations.Get(card_registration.mangopay_id)
        if settings.DEBUG:
            print('Card_registration_m:')
            print(card_registration_m)
        card_registration_m.RegistrationData = res
        card_registration_m = client.cardRegistrations.Update(card_registration_m)
        if settings.DEBUG:
            print('Card_registration_m:')
            print(card_registration_m)
            print('Status:')
            print(card_registration_m.Status)
            print('CardId')
            print(card_registration_m.CardId)
        card_registration.save_mangopay_card_id(card_registration_m.CardId)
        card_registration.mangopay_card.request_card_info()
        if settings.DEBUG:
            print('Card ID:')
            print(card_registration.mangopay_card.mangopay_id)
            print('Creation de MangoPayIn')

        return card_registration

    def make_payment(self, new_payment, project, amount_ttc, amount_tax):
        card_registration = self.save_card(new_payment)
        payin = MangoPayPayIn()
        payin.mangopay_user = card_registration.mangopay_user
        payin.mangopay_wallet= IdrilMangoPayWallet.objects.get(project__id=project.id)
        payin.mangopay_card = card_registration.mangopay_card
        if settings.DEBUG:
            print('CURRENCY')
            print(CURRENCY['EUR'].name)

        payin.create(secure_mode_return_url="https://www.idril.fr/payment/response",
                     debited_funds=PythonMoney(amount_ttc, CURRENCY['EUR']),
                     fees=PythonMoney(amount_tax, CURRENCY['EUR']))
        ''' payment is working -. To test in production (idril.fr to have a returned object'''


class IdrilMangoPayTransfer(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_debited_wallet = models.ForeignKey(
        IdrilMangoPayWallet, related_name="mangopay_debited_wallets")
    mangopay_credited_wallet = models.ForeignKey(
        IdrilMangoPayWallet, related_name="mangopay_credited_wallets")
    debited_funds = MoneyField(default=0, default_currency="EUR",
                               decimal_places=2, max_digits=12)
    execution_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9, choices=TRANSACTION_STATUS_CHOICES,
                             blank=True, null=True)
    result_code = models.CharField(null=True, blank=True, max_length=6)

    def create(self, fees=None):
        transfer = Transfer()
        transfer.DebitedWalletId = self.mangopay_debited_wallet.mangopay_id
        transfer.CreditedWalletId = self.mangopay_credited_wallet.mangopay_id
        transfer.AuthorId = self.mangopay_debited_wallet.mangopay_user.mangopay_id
        transfer.CreditedUserId = self.mangopay_credited_wallet.mangopay_user.mangopay_id
        transfer.DebitedFunds = python_money_to_mangopay_money(
            self.debited_funds)
        if not fees:
            fees = PythonMoney(0, self.debited_funds.currency)
        transfer.Fees = python_money_to_mangopay_money(fees)
        client = get_mangopay_api_client()
        created_transfer = client.transfers.Create(transfer)
        self._update(created_transfer)

    def get(self):
        client = get_mangopay_api_client()
        transfer = client.transfers.Get(self.mangopay_id)
        self._update(transfer)

    def _update(self, transfer):
        self.status = transfer.Status
        self.result_code = transfer.ResultCode
        self.mangopay_id = transfer.Id
        self.execution_date = get_execution_date_as_datetime(transfer)
        self.save()

def get_execution_date_as_datetime(mangopay_entity):
    execution_date = mangopay_entity.ExecutionDate
    if execution_date:
        formated_date = datetime.fromtimestamp(int(execution_date))
        if settings.USE_TZ:
            return formated_date.replace(tzinfo=utc)
        else:
            return formated_date