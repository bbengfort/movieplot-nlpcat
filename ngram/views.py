from django.views.generic import View
from django.http import HttpResponseRedirect
from movies.models import Movie
from ngram.analyze import MoviePlotAnalyzer

class MovieAnalyze(View):

    pk_kwarg = "movieid"
    analyzer = MoviePlotAnalyzer

    def post(self, request, *args, **kwargs):
        self.analyze()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.movie.get_absolute_url()

    def get_object(self):
        if self.pk_kwarg not in self.request.POST:
            raise Movie.DoesNotExist("No movie id specified to lookup plot to analyze.")
        pk = self.request.POST[self.pk_kwarg]
        return Movie.objects.get(pk=pk)

    def analyze(self):
        self.movie = self.get_object()
        if self.movie.ngram_analysis:
            self.movie.ngram_analysis.delete()
        self.ngram_analysis = self.analyzer.analyze(self.movie)
