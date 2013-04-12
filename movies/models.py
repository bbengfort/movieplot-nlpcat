from django.db import models
from movies.managers import *
from movieplot.core.utils import slugify

blank = { 'null': True, 'blank': True, 'default': None }

class Movie(models.Model):
    
    title        = models.CharField( max_length=255 )
    slug         = models.SlugField( max_length=355, unique=True, **blank )
    year         = models.CharField( max_length=4, **blank )
    rated        = models.CharField( max_length=32, **blank )
    released     = models.DateField( **blank )
    runtime      = models.CharField( max_length=64, **blank )
    genres       = models.ManyToManyField( 'Genre', related_name="movies" )
    directors    = models.ManyToManyField( 'Director', related_name="movies" )
    writers      = models.ManyToManyField( 'Writer', related_name="movies" )
    actors       = models.ManyToManyField( 'Actor', related_name="movies" )
    plot         = models.TextField( **blank )
    plot_simple  = models.TextField( **blank )
    poster_link  = models.CharField( max_length=255, **blank )
    poster       = models.ImageField( upload_to="posters", **blank )

    objects      = MovieManager()

    def get_slug(self):
        name = "%s %s" % (self.title, self.year)
        return slugify(name)

    @models.permalink
    def get_absolute_url(self):
        url_name = "MovieDetail"
        kwargs   = {'slug': self.slug}
        return (url_name, (), kwargs)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.get_slug()
        return super(Movie, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.year)

    class Meta:
        db_table = "movies"
        ordering = ("-year", "-released")
        get_latest_by = "released"

class Genre(models.Model):
    
    name         = models.CharField( max_length=255 )
    slug         = models.SlugField( max_length=355, unique=True, **blank )
    parent       = models.ForeignKey( 'self', on_delete=models.SET_NULL, **blank )

    def get_slug(self):
        return slugify(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.get_slug()
        return super(Genre, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "genres"

class Person(models.Model):
    
    name         = models.CharField( max_length=255 )
    slug         = models.SlugField( max_length=355 )

    def get_slug(self):
        return slugify(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.get_slug()
        return super(Person, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

class Director(Person):
    
    class Meta:
        db_table = "directors"

class Writer(Person):
    
    class Meta:
        db_table = "writers"

class Actor(Person):
    
    class Meta:
        db_table = "actors"
