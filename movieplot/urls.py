from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# DEBUGGING MEDIA FILES:
from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="index.html"), name='index'),
    url(r'^movies/', include('movies.urls')),
    url(r'^analyze/', include('ngram.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

# DEBUGGING MEDIA FILES:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
