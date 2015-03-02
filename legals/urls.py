__author__ = 'morgancollino'

from django.conf.urls import patterns, url

# URL planning a voir, juste prototype pour le moment.
urlpatterns = patterns('',
  url(r'^(?P<project_id>\d+)$', 'legals.views.informations'),
)
