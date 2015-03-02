from django.test import TestCase
from payment.models import Payment, PaypalInformations, BankInformations
from member.models import User
from project.models import Project
from project.models import Gift
# Create your tests here.


# Models units test


# PaymentTest
class PaymentTest(TestCase):
    def test_basic_payment(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        paypal = PaypalInformations()
        paypal.id = 64
        paypal.first_name = "TestCase"
        paypal.last_name = "TestCase"
        paypal.item_name = "TestCase"
        paypal.transaction_subject = "TestCase"
        paypal.pending_reason = "TestCase"
        paypal.payer_email = "TestCase@TestCase.com"
        paypal.tracking_id = "TestCase"

        print(paypal)

        bank = BankInformations()
        bank.id = 42
        bank.name_owner_card = "TestCase"
        bank.address = "TestCase address"
        bank.address2 = "TestCase address"
        bank.expiration_month = "12"
        bank.expiration_year = "12"
        bank.cryptogram = "73630001a95511bc5f72705b75bbd55860601cef81007c187f62df8ed0b972a24695efd4d8499ba9f887778542eadccd6fc578104058a67ea6e2d4a50faa685f09157c9022e7a9"
        bank.card_type = "VISA"
        bank.zip_code = "68210"
        bank.city = "DANNEMARIE"
        bank.country = "FRANCE"
        bank.card_number = "73630001026322218914dae4412041b75cdcc63d2fa91bb3f23037c51ec81c7c4b5ef328ab92266e53f32c22101d94160a8c0e0d9ac012e027c173be96540559d924cbdf8163fc1a46437271f54e2fefdfb8f346"

        print(bank)
        print(bank._card_number())
        print(bank._cvx())
        print(bank._expiration_data_mmaa())


        user = User()
        user.username = "TestCase"
        user.first_name = "TestCase"
        user.last_name = "TestCase"
        user.email = "TestCase@TestCase.com"

        user.is_staff = True

        print(user)

        project = Project()


        payment = Payment()
        payment.user = user
        payment.project = project
        payment.paypal_info = paypal
        payment.bank_info = bank
        payment.price = 42
        payment.tax = 0.42
        payment.payment_type = "CB"
        print(payment)
