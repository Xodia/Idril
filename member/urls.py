# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django.conf.urls import patterns, url

urlpatterns = patterns('',
  url(r'^$', 'member.views.member'),
  url(r'^login/$', 'member.views.login'),
  url(r'^auth/$', 'member.views.auth_view'),
  url(r'^logout/$', 'member.views.logout'),
  url(r'^profile/$', 'member.views.profile'),
  url(r'^register/$', 'member.views.register'),
  url(r'^messages/$', 'member.views.all_messages'),
  url(r'^password_change/$', 'member.views.password_change'),
  url(r'^messages/inbox/$', 'member.views.inbox_messages'),
  url(r'^payments/$', 'member.views.payments'),
  url(r'^messages/inbox/unread/$', 'member.views.inbox_unread_messages'),
  url(r'^messages/sent/$', 'member.views.sent_messages'),
  url(r'^messages/new_message/$', 'member.views.new_message'),
  url(r'^messages/markread/$', 'member.views.markread'),
  url(r'^messages/delete/$', 'member.views.delete'),
  url(r'^(?P<username>\w+)/$', 'member.views.profile_view'),

  url(r'^register/confirm/(?P<activation_key>.+)/$',
      'member.views.register_confirm', name='activation_key',),
  url(r'^delete_account/$', 'member.views.delete_account'),
  
  url(r'^password/reset/$', 'django.contrib.auth.views.password_reset',
      {'post_reset_redirect': '/member/password/reset/done/'}, name="password_reset"),
     (r'^password/reset/done/$', 'django.contrib.auth.views.password_reset_done'),
     (r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
      'django.contrib.auth.views.password_reset_confirm', {'post_reset_redirect': '/member/password/done/'}),
     (r'^password/done/$', 'django.contrib.auth.views.password_reset_complete'),
)
