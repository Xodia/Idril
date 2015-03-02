__author__ = 'morgancollino'

from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<project_id>[0-9]{1,4})/$', 'payment.views.index', name='index'),
    url(r'^choice/(?P<project_id>[0-9]{1,4})/(?P<gift_id>[-0-9]{1,4})/$', 'payment.views.payment_choice', name='choice'),
    url(r'^choice/$', 'payment.views.payment_choice', name='choice2'),
    url(r'^new$', 'payment.views.payment_cb', name='new'),
    url(r'^new/(?P<project_id>[0-9]{1,4})/(?P<gift_id>[-0-9]{1,4})/$', 'payment.views.payment_cb', name='new'),
    url(r'^list$', 'payment.views.payment_list', name='list'),
    url(r'^mypayments$', 'payment.views.payment_list_user', name='list_user'),
    url(r'^detail/(?P<payment_id>[0-9]{1,4})/$', 'payment.views.payment_detail', name='detail'),
    url(r'^refund/(?P<user_id>[0-9]{1,4})/(?P<payment_id>[0-9]{1,4})/$', 'payment.views.refund', name='refund'),
    url(r'^paypal$', 'payment.views.paypal', name='paypal'),
    url(r'^response$', 'payment.views.response', name='response'),
    url(r'^successfull/(?P<payment>\d+)/$', 'payment.views.successfull', name='successfull'),
    url(r'^paypal/return/(?P<user_id>[0-9]{1,4})/(?P<project_id>[0-9]{1,4})/(?P<gift_id>[-0-9]{1,4})/$', 'payment.views.return_paypal', name='return'),
    url(r'^paypal/cancel/(?P<user_id>[0-9]{1,4})/(?P<project_id>[0-9]{1,4})/(?P<gift_id>[-0-9]{1,4})/$', 'payment.views.cancel_paypal', name='cancel'),
    url(r'^paypal/you/re/not/gonna/find/me/coeur/idril/(?P<user_id>[0-9]{1,4})/(?P<project_id>[0-9]{1,4})/(?P<gift_id>[-0-9]{1,4})/$', 'payment.views.notify_paypal', name='notify'),
    url(r'^paypal/pdt/', include('paypal.standard.pdt.urls')),
)
