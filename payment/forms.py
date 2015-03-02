__author__ = 'morgancollino'

from django.forms import ModelForm
from models import Payment, BankInformations, PaypalInformations
from project.models import Gift
from django.core.exceptions import ValidationError
from binascii import hexlify, unhexlify
from simplecrypt import encrypt, decrypt
from django import forms
from django.core.validators import validate_integer
from django.conf import settings

COUNTRY_CHOICES = (
    ('USA', 'Etats-Unis'),
    ('FRANCE', 'France'),
    ('SUISSE', 'Suisse'),
    ('LUXEMBOURG', 'Luxembourg'),
    ('BELGIQUE', 'Belgique')
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

YEARS_EXP_CHOICES = (
    ('2015', 2015),
    ('2016', 2016),
    ('2017', 2017),
    ('2018', 2018),
    ('2019', 2019),
    ('2020', 2020)
)

CARD_CHOICES = (
    ('VISA', 'Visa'),
    ('MASTERCARD', 'MasterCard'),
    ('CB', 'Carte bleue'),
)

TYPE_CHOICES = (
    ('PAYPAL', 'Paypal'),
    ('CB', 'Carte bleue'),
    ('MANGOPAY', 'MangoPay')
)

STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('CANCELED', 'Canceled'),
    ('DENIED', 'Denied'),
    ('FAILED', 'Failed'),
    ('PAID', 'Paid'),
)

# class PaymentForm(ModelForm):
#    class Meta:
#        model = Payment
#        fields = ['first_name', 'last_name', 'title', 'address',
#        'address2', 'city', 'zip_code','state', 'country',
#        'cell_phone', 'nameOwnerCard', 'expirationMonth',
#        'expirationYear', 'cryptogram', 'cardType']
# ciphertext = encrypt(password, 'my secret')
# plaintext = decrypt(password, ciphertext)

class PaymentForm(ModelForm):

    gift = forms.ModelChoiceField(required=False, queryset=Gift.objects.all())
    price = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    tax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    payment_type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'btn btn-default btn-sm dropdown-toggle',
                                                                    'data-toggle': 'dropdown'}),
                                        required=False, choices=TYPE_CHOICES)
    payment_status = forms.ChoiceField(widget=forms.Select(attrs={'class': 'btn btn-default btn-sm dropdown-toggle',
                                                                    'data-toggle': 'dropdown'}),
                                        required=False, choices=STATUS_CHOICES)
    class Meta:
        model = Payment
        exclude = ('paypal_info', 'bank_info',)
        # fields = '__all__'

    def set_payment(self, type):
        data = self.data.copy()
        data['payment_type'] = type
        self.data = data
        print(self.data)


def luhn(n):
    r = [int(ch) for ch in str(n)][::-1]
    return (sum(r[0::2]) + sum(sum(divmod(d*2,10)) for d in r[1::2])) % 10 == 0


class BankInformationsForm(ModelForm):

    cryptogram = forms.IntegerField(widget=forms.TextInput(attrs={'size': 2, 'maxlength': 3, 'class': 'form-control',
                                                                  'placeholder': 'CVC'}),
                                    error_messages={'required': 'Veuillez renseigner le champ cryptogramme'})
    card_number = forms.CharField(widget=forms.TextInput(attrs={'size': 30, 'class': 'form-control',
                                                                'placeholder': 'Numero de carte'}),
                                  error_messages={'required': 'Veuillez renseigner le champ numero de carte bancaire'})
    name_owner_card = forms.CharField(widget=forms.TextInput(attrs={'size': 30, 'class': 'form-control',
                                                               'placeholder': 'Nom sur la carte'}), required=True,
                                      error_messages={'required': 'Veuillez renseigner le nom du titulaire de la carte'})
    address = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'class': 'form-control',
                                                            'placeholder': 'Adresse'}), required=True,
                              error_messages={'required': 'Veuillez renseigner votre adresse'})
    address2 = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'class': 'form-control',
                                                             'placeholder': 'Adresse 2'}), required=False)
    city = forms.CharField(widget=forms.TextInput(attrs={'size': 30, 'class': 'form-control',
                                                         'placeholder': 'Ville'}), required=True,
                           error_messages={'required': 'Veuillez renseigner la ville'})
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'size': 10, 'maxlength': 6, 'class': 'form-control',
                                                             'placeholder': 'Code postal'}), required=True,
                               error_messages={'required': 'Veuillez renseigner le champ code postal'})
    expiration_month = forms.ChoiceField(widget=forms.Select(attrs={'maxlength': 2,
                                                                    'class': 'btn btn-default btn-sm dropdown-toggle',
                                                                    'data-toggle': 'dropdown'}),
                                         required=True, choices=MONTH_EXP_CHOICES)
    expiration_year = forms.ChoiceField(widget=forms.Select(attrs={'maxlength': 4,
                                                                   'class': 'btn btn-default btn-sm dropdown-toggle',
                                                                    'data-toggle': 'dropdown'}),
                                        required=True, choices=YEARS_EXP_CHOICES)
    country = forms.ChoiceField(widget=forms.Select(attrs={'maxlength': 4,
                                                                   'class': 'btn btn-default btn-sm dropdown-toggle',
                                                                    'data-toggle': 'dropdown'}),
                                required=True, choices=COUNTRY_CHOICES)
    card_type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'btn btn-default btn-sm dropdown-toggle',
                                                                    'data-toggle': 'dropdown'}),
                                required=True, choices=CARD_CHOICES)
    class Meta:
        model = BankInformations
        exclude = ('',)
        # fields = '__all__'

    def clean_name_owner_card(self):
        data = self.cleaned_data['name_owner_card']
        #encrypt(PAYMENT_HASH, self.cleaned_data['last_name'])
        return data.upper()

    def clean_address(self):
        data = self.cleaned_data['address']
        return data.upper()

    def clean_address2(self):
        data = self.cleaned_data['address2']
        return data.upper()

    def clean_city(self):
        data = self.cleaned_data['city']
        return data.upper()

    def clean_country(self):
        data = self.cleaned_data['country']
        return data.upper()

    def clean_cryptogram(self):
        data = self.cleaned_data['cryptogram']
        print(len(str(data)))
        if len(str(data)) <= 3:
            if len(str(data)) > 3 or len(str(data)) < 3:
                raise ValidationError("Erreur: Cryptogramme invalide")
            if validate_integer(data) is False:
                raise ValidationError("Erreur: Cryptogramme invalide")
            return hexlify(encrypt(settings.PAYMENT_HASH, str(data)))
        return data

    def clean_card_number(self):
        data = self.cleaned_data['card_number']
        print('LEN(DATA)-->')
        print(len(data))
        if len(data) >= 12 and len(data) < 20:# len between 12 and 19 digits
            res = luhn(data)
            if not res:
                raise ValidationError("Erreur: Numero de carte de credit invalide.")
            return hexlify(encrypt(settings.PAYMENT_HASH, data))
        else:
            raise ValidationError("Erreur: Numero de carte de credit invalide.")
        return data

    def __init__(self, *args, **kwargs):
        super(BankInformationsForm, self).__init__(*args, **kwargs)

class PaypalInformationsForm(ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    payer_status = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    payment_status = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    tracking_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    payer_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    item_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    payer_email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    transaction_subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    pending_reason = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    receiver_email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    payment_date = forms.DateTimeField(required=False)



    class Meta:
        model = PaypalInformations
        exclude = ('',)
        # fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(PaypalInformationsForm, self).__init__(*args, **kwargs)

class PaymentCreationForm(ModelForm):
    class Meta:
        model = Payment
        exclude = ('paypal_info', 'bank_info', 'tax', 'payment_type', 'payment_status',)

    def __init__(self, *args, **kwargs):
        super(PaymentCreationForm, self).__init__(*args, **kwargs)