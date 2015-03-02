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

'''

This is the basic information you are required to collect from your users in order to process payments (Cash-in / Cash-out). We cannot allow any transactions from a user who has not provided the following information:

1000euros DEBIT (+) 2500euros CREDIT (-)

For a customer (NATURAL_PERSON):

ASK @INSCRIPTION ?
Email
FirstName
LastName
Country of Residence
Birthday
Nationality


For a business or organization (LEGAL_PERSON):
Legal Person Type (BUSINESS or ORGANIZATION)
Business Name
Generic business email
FirstName of the legal representative
LastName of the legal representative
Birthday of the legal representative
Nationality of the legal representative
Country of residence of the legal representative


MORE :

This is the information you are required to collect from your users to go over the Cash-in (2.500euro)  and/or Cash-out (1.000euro)limits:

For a customer (NATURAL_PERSON).

In addition to the Light Authentication fields
Address (declarative field)
ID Card (1) (Proof Of Identity)
Occupation (2) (declarative field)
Income Range (2) (declarative field)
For a business companies (LEGAL_PERSON).
In addition to the Light Authentication fields
Headquarter address (declarative field)
Legal Representative email
Legal Representative Address
Certified articles of association (Statute) : formal memorandum stated by the entrepreneurs, in which the following information is mentioned:business name, activity, registered address, shareholding..
Proof of registration: Extract from the Company Register issued within the last three months (4)
Send the Shareholder declaration
The ID of the individual duly empowered to act on behalf of the legal entity
For Organizations (LEGAL_PERSON).
In addition to the Light Authentication fields

Headquarter address (declarative field)
Legal Representative email
Legal Representative Address
ID of the individual duly empowered to act on behalf of the legal entity
Certified articles of association (Statute)
Proof of registration from the official authority


STRONG:

This is the information required for users suspected of fraud, money laundering, terrorism, politically exposed people:

For a customer (NATURAL_PERSON).
To be added to Light & Regular Authentication fields
Confirmation of residence (3) (Proof Of Address)


For a business or organization (LEGAL_PERSON).
To be added to Light & Regular Authentication fields
Confirmation of bank details

Lien: https://docs.mangopay.com/api-references/kyc-rules/

'''


@login_required()
def informations(request, project_id):

    category = 0
    project = Project.objects.get(id=project_id)

    if project.user.id != request.user.id and request.user.is_staff != 1:
        raise Http404

    if project.amount_required > 1000:
        category = 1
    elif project.amount_required <= 1000:
        category = 0


    return render(request, 'legals/informations.html',
        {'category': category})
