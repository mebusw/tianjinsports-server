from django.conf.urls import patterns, include, url

urlpatterns = patterns('polls.views',
    url(r'^$', 'index'),
    url(r'^jsonp$', 'jsonp'),
    url(r'^(?P<poll_id>\d+)/$', 'detail'),
    url(r'^(?P<poll_id>\d+)/results/$', 'results'),
    url(r'^(?P<poll_id>\d+)/vote/$', 'vote'),

    url(r'^wx_main$', 'wx_main'),

)