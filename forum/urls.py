# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django.conf.urls import patterns, url

urlpatterns = patterns('',
  url(r'^$', 'forum.views.home'),
  url(r'^create_topic/$', 'forum.views.create_topic'),
  url(r'^topic/(?P<id>\d+)/$', 'forum.views.topic'),
  url(r'^topic/(?P<id>\d+)/reply$', 'forum.views.reply_message'),
  url(r'^topic/(?P<id>\d+)/report$', 'forum.views.report_message'),
  url(r'^topic/(?P<id>\d+)/like$', 'forum.views.like_message'),
  url(r'^topic/(?P<id>\d+)/dislike$', 'forum.views.dislike_message'),
  url(r'^topic/(?P<id>\d+)/post_message$', 'forum.views.post_message'),
)
