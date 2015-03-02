__author__ = 'morgancollino'
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

@staff_member_required
def index(request):

    return render_to_response('administration/index.html',{},
                              context_instance=RequestContext(request))

def error404(request):

    return render_to_response('administration/error404.html', {}, context_instance=RequestContext(request))

def error500(request):

    return render_to_response('administration/error500.html', {}, context_instance=RequestContext(request))

def error403(request):

    return render_to_response('administration/error403.html', {}, context_instance=RequestContext(request))