# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django.shortcuts import render
from project.models import Project
from django.views.decorators.cache import cache_page
from mangopay_idril.models import IdrilMangoPayTransfer
import operator

def home(request):
    projects = Project.objects.order_by('-date').filter(state='1')[:4]
    ordered = sorted(projects, key=operator.attrgetter('category.name')) # Plus rapide que de faire
                                                                         # un in a chaque fois dans la boucle plus bas pour verifier si une clef existe ?
    category = ''
    final = {}
    for p in ordered:
        percent = p.get_percentage
        if p.category.name != category:
            category = p.category.name
            final[category] = [{p: percent}]
        else:
            final[category].append({p: percent})
    return render(request, 'base/index.html',
                  {'grouped_projects': final,})