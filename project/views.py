# -*- coding: utf8 -*-

from __future__ import unicode_literals
from datetime import date
import operator

from django.http import HttpResponseRedirect
from django.shortcuts import render
import bleach

from django.contrib.auth.decorators import login_required
from django.core.exceptions import *

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from member.models import Address

from project.models import Project
from project.models import ProjectComment
from project.models import Gift
from project.models import ProjectCategory
from project.forms import ProjectFormEdit
from project.forms import ProjectFormCreate
from project.forms import GiftFormSetCreate
from project.forms import AddCommentForm
from mangopay_idril.models import IdrilMangoPayWallet, IdrilMangoPayUser


def home(request):
    #ordered = sorted(projects, key=operator.attrgetter('category.name')) # Plus rapide que de faire
    amount = 0                                                                     # un in a chaque fois dans la boucle plus bas pour verifier si une clef existe ?
    categories = ProjectCategory.objects.all()
    selected_category = categories.first()
    print request.POST
    if request.method == 'POST':
        post = request.POST
        if 'selected_category' in post:
            try:
                selected_category = ProjectCategory.objects.all().get(name=post.get('selected_category'))
            except:
                selected_category = categories.first()
    if selected_category is None:
        nb_project_category = 0
        projects = None
    else:
        nb_project_category = Project.objects.all().filter(category__id=selected_category.id).filter(state='1').count()
        projects = Project.objects.all().filter(category__id=selected_category.id).filter(state__in=['1', '2', '3']).order_by('-date')[:3]
    return render(request, 'project/project_view.html', {'projects': projects, 'project_amount': amount
                        ,'categories': categories, 'selected_category': selected_category,
                                                         'nb_project_category': nb_project_category})


def details(request, id):
    project = get_object_or_404(Project, id=id)
    if request.user.is_staff == False and project.state == '4':
        return redirect('/project')
    comments = ProjectComment.objects.filter(project = project)
    amount = project.get_funds_for_project()
    percent = (amount / project.amount_required) * 100
    percent = "%.2f" % percent
    days = (project.end_date-project.date).days
    isCreator = project.user.id == request.user.id or request.user.is_staff == 1
    comment_form = AddCommentForm(prefix='comment')
    return render(request, 'project/project_details.html',
                  {'project': project, 'percent': percent, 'amount': amount,
                   'days': days, 'isCreator': isCreator, 'comments': comments, 'comment_form': comment_form})

@login_required
def edit(request, id):
    project = Project.objects.get(id=id)
    if request.method == 'POST':
        form = ProjectFormEdit(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project.date_modified = date.today()
            form.save()
            return HttpResponseRedirect('/project/project_' + str(project.id))
    else:
        form = ProjectFormEdit(instance=project)
    return render(request, 'project/project_edit.html',
                  {'project': project, 'form': form})

@login_required
def create(request):
    # A user must have some info set to create a project
    user = request.user
    try:
        user_address = Address.objects.get(user=user)
    except Exception:
        user_address = None
    if not user.first_name or not user.last_name or not user.email \
       or not user_address.street1 or not user_address.zip_code \
       or not user_address.city or not user_address.phone_number1:
        return render(request, 'project/project_more_info.html')

    categories = ProjectCategory.objects.all()
    if request.method == 'POST':
        project_form = ProjectFormCreate(request.POST, request.FILES, prefix='project')
        gift_formset = GiftFormSetCreate(request.POST, prefix='gift')
        if project_form.is_valid() and gift_formset.is_valid():
            project = project_form.save(commit=False)
            project.user = request.user
            # project.content = bleach.clean(project.content, tags=('div', 'p', 'strong', 'em', 'span', 'ul', 'li'),
            #                                                 attributes={
            #                                                 '*': ['class', 'style'],
            #                                                 'a': ['href', 'rel'],
            #                                                 'img': ['src', 'alt'],
            #                                                 }) # Cleans HTML. Have to look further for efficiency...

            gifts = gift_formset.save()
            project.state = '4'
            project.save()
            project.gifts = gifts
            project.save()

            # Creation d'un porte-feuille pour le projet - 1 wallet/projet
            try:
                user = IdrilMangoPayUser.objects.get(user__id=request.user.id)
                wallet = IdrilMangoPayWallet()
                wallet.create_wallet(user, project)
            except Exception as e:
                user = 0
                print(e)
            return HttpResponseRedirect('/project')
    else:
        project_form = ProjectFormCreate(prefix='project')
        gift_formset = GiftFormSetCreate(prefix='gift', queryset=Gift.objects.none())
    return render(request, 'project/project_create.html',
                  {'project_form': project_form, 'categories': categories,
                   'gift_formset': gift_formset})

def list_category(request, category_id):
    category = ProjectCategory.objects.all().get(id=category_id)
    projects = Project.objects.all().filter(category__id=category.id).filter(state='1').order_by('-date')
    return render(request, 'project/project_list.html', {'projects': projects, 'category': category})


def list_projects(request):
    projects = list()
    search = ''
    if request.method == 'GET':
        get = request.GET
        if 's' in get:
            projects = Project.objects.all().filter(title__icontains=get.get('s')).filter(state__in=['1', '2', '3']).order_by('-date')
            search = get.get('s')
    return render(request, 'project/project_search.html', {'projects': projects, 'search': search })

@login_required
def add_comment(request, id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=id)
        comment_form = AddCommentForm(request.POST, prefix='comment')
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.project = project
            comment.save()
            return redirect('/project/project_'+id)
    return redirect('/project/project_'+id)
