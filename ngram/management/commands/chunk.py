__author__ = 'benjamin'

from movies.models import Movie
from ngram.analyze import MoviePlotAnalyzer
from django.core.management import BaseCommand, CommandError

class Command(BaseCommand):

    analyzer = MoviePlotAnalyzer

    help = "Creates NGram Models for all movies in the database, deleting previous analyses."

    def handle(self, *args, **options):

        self.verbosity = int(options.get('verbosity', 1))

        for movie in Movie.objects.select_related('ngram_analysis').all():
            if movie.ngram_analysis:
                movie.ngram_analysis.delete()
            analysis = self.analyzer.analyze(movie)

            if self.verbosity > 0:
                print analysis