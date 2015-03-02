# -*- coding: utf8 -*-

from __future__ import unicode_literals
from datetime import date
from datetime import datetime, timedelta
from django.db.models import Sum

import operator

from django.http import HttpResponseRedirect
from django.shortcuts import render
import bleach
from django.contrib.auth.decorators import login_required
from project.models import Project
from payment.models import Payment
from member.models import User
from mangopay_idril.models import IdrilMangoPayWallet, IdrilMangoPayUser
from django.http import Http404


@login_required()
def home(request, id):

    project = Project.objects.get(id=id)

    if project.user.id != request.user.id and request.user.is_staff != 1:
        raise Http404

    amount = project.get_funds_for_project()
    percent = (amount / project.amount_required) * 100
    percent = "%.2f" % percent
    days = (project.end_date-project.date).days
    daysTilToday = (datetime.now().date()-project.date).days + 1
    today = datetime.now()
    last_payments = Payment.objects.order_by('-payment_date').filter(project__id=id)[:5]
    tax = Payment.objects.filter(project__id=id).aggregate(Sum('tax'))

    total = 0
    if tax['tax__sum'] is not None:
        total = amount - tax['tax__sum']

    _last_users = Payment.objects.filter(project__id=id).values('user__id').distinct()

    last_users = []
    for userDic in _last_users:
        user = User.objects.get(id=userDic['user__id'])
        last_users.append(user)

    values = Payment.objects.values('payment_date').annotate(data_sum=Sum('price')).filter(payment_date__range=(project.date,datetime.now()), project__id=id)
    array_days = []
    for i in range(0, daysTilToday):
        new_date = project.date
        new_date = new_date + timedelta(days=i)
        didAppend = 0
        for o in values:
            if new_date == o['payment_date'].date():
                didAppend = 1
                obj = {'date': new_date.strftime("%Y-%m-%d"), 'value': o['data_sum']}
                print obj
                array_days.append(obj)

        if didAppend == 0:
            obj = {'date': new_date.strftime("%Y-%m-%d"), 'value': 0}
            print obj
            array_days.append(obj)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            project.stop()

    return render(request, 'manager/home.html',
        {'project': project, 'percent': percent, 'days': daysTilToday, 'today': today, 'values': array_days,
         'last_payments': last_payments, 'last_users': last_users, 'tax': tax, 'totalTTC': total})
