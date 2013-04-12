import re

from models import *
from urllib2 import urlopen
from urllib import urlencode
from datetime import datetime
from django.db import connection
from django.utils import simplejson as json
from httplib import HTTPConnection, HTTPException
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

class IMDBException(Exception):
    """
    Abstract class to deal with lookup errors.
    """
    pass

class IMDBHttpException(IMDBException):
    """
    Abstract class for IMDB Http issues.
    """

    def __init__(self, code=500, error=None):
        self.code    = code
        self.message = error

    def __str__(self):
        return "Error %s: %s" % (self.code, self.message)

class MovieApi(object):
    
    VERB = "GET"
    HOST = "imdbapi.org"
    URI  = "/"

    def __init__(self, **kwargs):

        # Add any addtional params to query or override defaults
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)

    def search(self, title, limit=10):
        return self.get({'title': title, 'limit':limit })

    def get(self, query):
        """
        Executes a lookup request for the given query, which should be a
        ``dict`` of name value pairs to pass to the api.
        
        :: returns :: A JSON object
        """
        request  = self.encode(query)
        
        try:
            try:
                conn = HTTPConnection(self.HOST)
                conn.request(self.VERB, "?".join([self.URI, request]))
            except HTTPException as e:
                raise IMDBException("Could not connect to Movie API: %s" % str(e))

            try:
                response = conn.getresponse()
                response = json.load(response)
            except ValueError as e:
                raise IMDBException("Could not parse response from Movie API: %s" % str(e))
            
            if 'error' in response:
                raise IMDBHttpException(**response)

            conn.close()
            return response

        except Exception as e:
            conn.close()
            raise e 

    def encode(self, query):
        """
        Encodes a query ``dict`` for a url query string, and adds default
        parameters from the get_default_params method on this class.
        """
        params   = self.get_request_params(**query)
        return urlencode(params)

    def get_request_params(self, **kwargs):
        """
        Creates a dictionary of default parameters to pass to the API, any
        key word arguments passed to this class will be added to the query
        string, overriding any defaults. 
        """
        params = {
            'type': 'json',
            'plot': 'full',
            'episode': 0,
            'limit': 10,
            'yg': 0,
            'mt': 'none',
            'lang': 'en-US',
            'aka': 'simple',
            'release': 'simple',
            'business': 0,
            'tech': 0,
        }
        params.update(kwargs)
        return params

class Scraper(object):
    
    def __init__(self, path="fixtures/title_list.txt"):
        self.api    = MovieApi()
        self.path   = path
        self.timere = re.compile(r'^(\d{4})(\d{2})(\d{2})$')

    def __iter__(self):
        with open(self.path, 'r') as titles:
            for title in titles:
                yield title.strip()

    def valid_data(self, key, data):
        if key in data:
            item = data[key]
            if item is not None:
                if item != "" and item != {} and item != []:
                    return True
        return False

    def lookup_name(self, name, model):
        queryset = model.objects.filter(name__iexact=name)
        if len(queryset) > 1:
            return queryset[0]
        else:
            return model.objects.create(name=name)

    def parse_datetime(self, time):
        if isinstance(time, int):
            time = str(time)
        
        pattern = self.timere.match(time)
        if pattern:
            dargs = [int(x) if x !="00" else 1 for x in pattern.groups()]
            return datetime(*dargs)
        return None

    def movie_with_json(self, data):
        
        if 'title' not in data:
            raise Exception("Required field 'title' is missing")

        try:
            movie = Movie.objects.get(title__iexact=data['title'])
        except Movie.DoesNotExist:
            movie = Movie(title=data['title'])

        # Update with JSON data
        if self.valid_data('year', data):         movie.year        = data['year']
        if self.valid_data('rated', data):        movie.rated       = data['rated']
        if self.valid_data('release_date', data): movie.released    = self.parse_datetime(data['release_date'])
        if self.valid_data('runtime', data):      movie.runtime     = data['runtime'][0]
        if self.valid_data('plot', data):         movie.plot        = data['plot']
        if self.valid_data('plot_simple', data):  movie.plot_simple = data['plot_simple']
        if self.valid_data('poster', data):       movie.poster_link = data['poster']

        movie.save()

        # Update Many to Many fields
        if self.valid_data('genres', data):
            for name in data['genres']:
                movie.genres.add(self.lookup_name(name, Genre))

        if self.valid_data('directors', data):
            for name in data['directors']:
                movie.directors.add(self.lookup_name(name, Director))

        if self.valid_data('writers', data):
            for name in data['writers']:
                movie.writers.add(self.lookup_name(name, Writer))

        if self.valid_data('actors', data):
            for name in data['actors']:
                movie.actors.add(self.lookup_name(name, Actor))

        return movie

    def scrape(self, save=True, verbose=True):
        counts = {
            'saves': 0,
            'error': 0,
        }

        data = []

        for title in self:
            try:
                data = self.api.search(title)
                if data:
                    for item in data:
                        if save:
                            movie = self.movie_with_json(item)
                            counts['saves'] += 1
                            if verbose:
                                print movie
                        else:
                            data.append(item)
            except Exception as e:
                connection._rollback()      # PostgreSQL rollback mechanism
                counts['error'] += 1              
                if verbose:
                    print "Exception searching for \"%s\": %s" % (title, str(e))
                continue

        if not save:
            with open('fixtures/title_list.json', 'w') as out:
                json.dump(data, out)

        print "%(saves)i movies saved, %(error)i titles skipped." % counts

class PosterScraper(object):

    def execute(self, url):
        """
        Executes a URL request to a full URL.
        """
        try:
            request = urlopen(url)
            tempimg = NamedTemporaryFile(delete=True)

            tempimg.write(request.read())
            tempimg.flush()

            request.close()
            return File(tempimg)
        except Exception as e:
            raise IMDBHttpException("Could not fetch image: %s" % str(e))

    def fetch(self, movie):
        if not movie.poster_link:
            return False

        poster = self.execute(movie.poster_link)
        if poster.size > 0:
            extension   = movie.poster_link.split(".")[-1].lower()
            if extension not in ('jpg', 'jpeg', 'png', 'gif'):
                raise Exception("Unknown image extension '%s'" % extension)
            poster_name = "%s.%s" % (movie.get_slug(), extension)
            movie.poster.save(poster_name, poster, True)

        del poster
        return True

    def scrape(self, force=False, verbose=True):
        counts = {
            'saves': 0,
            'error': 0,
            'noimg': 0,
            'skip':  0,
            }

        for movie in Movie.objects.all():
            try:
                if movie.poster and not force:
                    counts['skip'] += 1
                    continue

                if self.fetch(movie):
                    counts['saves'] += 1
                else:
                    counts['noimg'] += 1
            except Exception as e:
                connection._rollback()
                counts['error'] += 1

                if verbose:
                    print "Exception fetching image for \"%s\": %s" % (movie.title, str(e))
                continue

        print "%(saves)i posters fetched, %(error)i posters errors, and %(skip)i skipped, %(noimg)i movies had no poster links." % counts

if __name__ == "__main__":

    scraper = Scraper()
    scraper.scrape(save=False)
