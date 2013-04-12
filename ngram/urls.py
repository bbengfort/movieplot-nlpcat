from ngram.views import *
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^movie/$', MovieAnalyze.as_view(), name=MovieAnalyze.__name__),
)