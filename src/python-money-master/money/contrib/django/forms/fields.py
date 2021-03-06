from django.utils.translation import ugettext_lazy as _
from django import forms
from widgets import CurrencySelectWidget
from money import Money, CURRENCY

class MoneyField(forms.MultiValueField):
    def __init__(self, choices=None, decimal_places=2, max_digits=12, *args, **kwargs):
        # Note that we catch args and kwargs that must only go to one field
        # or the other. The rest of them pass onto the decimal field.
        choices = choices or list(( (u"%s" % (c.code,), u"%s - %s" % (c.code, c.name)) for i, c in sorted(CURRENCY.items()) if c.code != 'XXX'))

        self.widget = CurrencySelectWidget(choices)

        fields = (
            forms.DecimalField(*args,
                decimal_places=decimal_places,
                max_digits=max_digits,
                **kwargs),
            forms.ChoiceField(choices=choices)
        )
        super(MoneyField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        """
        Take the two values from the request and return a single data value
        """
        if data_list:
            return Money(*data_list)
        return None
