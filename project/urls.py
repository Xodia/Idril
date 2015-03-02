from django.conf.urls import patterns, url

# URL planning a voir, juste prototype pour le moment.
urlpatterns = patterns('',
  url(r'^$', 'project.views.home'),
  url(r'^project_(?P<id>\d+)/$', 'project.views.details'),
  url(r'^project_(?P<id>\d+)/edit/$', 'project.views.edit'),
  url(r'^create/$', 'project.views.create'),
  url(r'^category/(?P<category_id>[0-9]{1,4})/$', 'project.views.list_category'),
  url(r'^search$', 'project.views.list_projects'),
  url(r'^project_(?P<id>\d+)/add_comment/$', 'project.views.add_comment'),
)
