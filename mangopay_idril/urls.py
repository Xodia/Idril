from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^list', 'mangopay_idril.views.list', name='list'),
    url(r'^wallets', 'mangopay_idril.views.wallets', name='wallets'),
    url(r'^users', 'mangopay_idril.views.users', name='users'),
    url(r'^wallet/(?P<project_id>[0-9]{1,4})/$', 'mangopay_idril.views.wallet', name='wallet'),
    url(r'^wallet_user/(?P<user_id>[0-9]{1,4})/$', 'mangopay_idril.views.wallet_personal', name='wallet_personal'),
)