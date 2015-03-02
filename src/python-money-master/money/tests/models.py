from django.db import models
from money.contrib.django.models.fields import *
from money import Money


class TestMoneyModel(models.Model):
    name = models.CharField(max_length=100)
    price = MoneyField(max_digits=12, decimal_places=3)

    def __unicode__(self):
        return self.name + " " + str(self.price)


class TestMoneyModel_0_USD(models.Model):
    name = models.CharField(max_length=100)
    price = MoneyField(max_digits=12, decimal_places=3, default=Money(0, "USD"))

    def __unicode__(self):
        return self.name + " " + str(self.price)


class TestMoneyModel_USD(models.Model):
    name = models.CharField(max_length=100)
    price = MoneyField(max_digits=12, decimal_places=3, default_currency="USD")

    def __unicode__(self):
        return self.name + " " + str(self.price)
