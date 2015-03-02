# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url

urlpatterns = patterns('',
  url(r'^$', 'administration.views.index'),
  url(r'^member/$', 'member.admin.member_list'),
  url(r'^member/(?P<username>\w+)/$', 'member.admin.edit_member'),
  url(r'^project/$', 'project.admin.project_list'),
  url(r'^project/(?P<id>\d+)/(?P<action>\w+)/$', 'project.admin.project_action'),
)
