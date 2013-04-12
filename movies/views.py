import time

from movies.models import *
from django.views.generic import ListView, DetailView

class MovieSearch(ListView):

    model = Movie
    template_name = "search.html"
    context_object_name = "results"
    paginate_by = 20
    query = None

    def get(self, request, *args, **kwargs):
        self.query = request.GET.get('query', None)
        return super(MovieSearch, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.search(self.query)

    def get_context_data(self, **kwargs):
        start   = time.time()
        context = super(MovieSearch, self).get_context_data(**kwargs)

        # Save query in context for template access
        context['query'] = self.query

        # Get the URL for pagination
        pqd = self.request.GET.copy()
        if 'page' in pqd: del pqd['page']
        context['pqdurl'] = pqd.urlencode()

        # Calculate the time required
        finit = time.time()
        delta = finit - start
        context['query_time'] = "%0.5f" % delta

        return context

class MovieDetail(DetailView):

    model = Movie
    template_name = "movie-detail.html"
    context_object_name = "movie"
