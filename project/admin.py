# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib.admin.views.decorators import staff_member_required 
from django.shortcuts import render_to_response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from project.models import Project, ProjectCategory, Funding, Gift, ProjectComment

# Register your models here.
admin.site.register(Project)
admin.site.register(ProjectCategory)
admin.site.register(Funding)
admin.site.register(Gift)
admin.site.register(ProjectComment)

@staff_member_required
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'administration/project_list.html', {'projects': projects})

@staff_member_required
def project_action(request, id, action):
    project = get_object_or_404(Project, id=id)
    if project.state == '4' and (action == '1'  or action == '0'): # WAITING
        project.state = action
        project.save()
    elif project.state == '1' and (action == '4'  or action == '0'):
        project.state = action
        project.save()
    elif project.state == '0' and action == '1':
        project.state = action
        project.save()
    return redirect('/administration/project')
