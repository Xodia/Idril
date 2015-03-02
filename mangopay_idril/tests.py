from django.test import TestCase
from mangopay.models import MangoPayNaturalUser, MangoPayWallet
from django.db import models
from member.models import User
from project.models import Project
from mangopay.models import MangoPayCardRegistration
from mangopay.client import get_mangopay_api_client
from mangopay.models import (MangoPayPayIn)
from mangopay_idril.models import IdrilMangoPayUser, IdrilMangoPayWallet
from money import Money as PythonMoney, CURRENCY
from mangopaysdk.types.exceptions.responseexception import ResponseException
import datetime

from project.models import Gift
# Create your tests here.


# Models units test


# PaymentTest
class MangoPayTest(TestCase):
    def test_basic_payment(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        user = User()
        user.id = 42
        user.username = "TestCase"
        user.first_name = "TestCase"
        user.last_name = "TestCase"

        project = Project()
        project.id = 42
        project.title = "TestCase"
        project.content = "Content - TestCase"
        project.end_date = datetime.datetime.utcnow()

        wallet = IdrilMangoPayWallet().create_wallet(user, project)
        print(wallet)

        mango_user = IdrilMangoPayUser().create_user(user, "FRANCE", "FRANCE", datetime.datetime.utcnow())
        print(mango_user)
