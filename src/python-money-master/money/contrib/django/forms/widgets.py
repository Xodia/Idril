from django import forms
from money import Money, CURRENCY
from decimal import Decimal

class CurrencySelectWidget(forms.MultiWidget):
    """
    Custom widget for entering a value and choosing a currency
    """
    def __init__(self, choices=None, attrs=None):
        widgets = (
            forms.TextInput(attrs=attrs),
            forms.Select(attrs=attrs, choices=choices),
        )
        super(CurrencySelectWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        #print "CurrencySelectWidget decompress %s" % value
        if value:
            return [value.amount, value.currency]
        return [None,None]
