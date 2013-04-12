from movies.views import *
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', MovieSearch.as_view(), name=MovieSearch.__name__),
    url(r'^(?P<slug>[-\w]+)/$', MovieDetail.as_view(), name=MovieDetail.__name__),
)