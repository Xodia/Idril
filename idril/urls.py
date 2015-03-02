# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('base.urls')),
    url(r'^forum/', include('forum.urls')),
    url(r'^member/', include('member.urls')),
    url(r'^project/', include('project.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^payment/', include('payment.urls')),
    url(r'^administration/', include('administration.urls')),
    url(r'^mangopay/', include('mangopay_idril.urls')),
    url(r'^manager/', include('manager.urls')),
    url(r'^legals/', include('legals.urls')),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))

handler404 = 'administration.views.error404'
handler403 = 'administration.views.error403'
handler500 = 'administration.views.error500'
