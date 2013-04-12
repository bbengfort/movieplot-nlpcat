from django.db import models
from ngram.managers import NGramManager
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

UNIGRAM = 'Unigram'
BIGRAM  = 'Bigram'
TRIGRAM = 'Trigram'

class NGram(models.Model):

    objects      = NGramManager()
    ngram_models = generic.GenericRelation( 'NGramModel', content_type_field='ngram_type', object_id_field='ngram_id' )

    def get_corpus_frequency(self):
        count = 0
        for frequency in self.ngram_models.values('frequency'):
            count += frequency['frequency']
        return count

    class Meta:
        abstract = True

class Unigram(NGram):

    token = models.CharField( max_length=100, unique=True )

    def natural_key(self):
        return self.token

    def __unicode__(self):
        return self.token

    class Meta:
        ordering = ("token",)

class Bigram(NGram):

    alpha = models.ForeignKey( Unigram, related_name="bigrams" )
    beta  = models.ForeignKey( Unigram, related_name="+" )

    def natural_key(self):
        return (self.alpha, self.beta)

    def __getitem__(self, idx):
        if idx == 0:
            return self.alpha
        elif idx == 1:
            return self.beta
        else:
            raise IndexError("Bigrams do not have an index '%s'" % str(idx))

    def __repr__(self):
        return "<Bigram %s>" % unicode(self)

    def __unicode__(self):
        return "(%s, %s)" % (self.alpha, self.beta)

    class Meta:
        unique_together = ('alpha', 'beta')
        ordering = ('alpha', 'beta')

class Trigram(NGram):

    alpha = models.ForeignKey( Unigram, related_name="trigrams" )
    beta  = models.ForeignKey( Unigram, related_name="+" )
    gamma = models.ForeignKey( Unigram, related_name="+" )

    def natural_key(self):
        return (self.alpha, self.beta, self.gamma)

    def __getitem__(self, idx):
        if idx == 0:
            return self.alpha
        elif idx == 1:
            return self.beta
        elif idx == 2:
            return self.gamma
        else:
            raise IndexError("Trigrams do not have an index '%s'" % str(idx))

    def __repr__(self):
        return "<Trigram %s>" % unicode(self)

    def __unicode__(self):
        return "(%s, %s, %s)" % (self.alpha, self.beta, self.gamma)

    class Meta:
        unique_together = ('alpha', 'beta', 'gamma')
        ordering = ('alpha', 'beta', 'gamma')

NGRAM_TYPE_MAP = {
    UNIGRAM: Unigram,
    BIGRAM: Bigram,
    TRIGRAM: Trigram,
}

class NGramModel(models.Model):
    """
    Utilizes the contenttypes contrib to generically hold a frequency for
    some generic object- in this case either a Unigram, a Bigram, or a
    Trigram - identified by the ngram_id and ngram_type. Access is simple
    through the ngram item on the model.

    @todo: make analysis another generic type, as in this model can be
    applied to any other model that has some text field inside of it, then
    set up a generic Analysis object for content types to use.
    """

    frequency  = models.IntegerField( default=1 )
    ngram_type = models.ForeignKey(ContentType)
    ngram_id   = models.PositiveIntegerField()
    ngram      = generic.GenericForeignKey('ngram_type', 'ngram_id')
    analysis   = models.ForeignKey( 'NGramPlotAnalysis', related_name='ngram_model' )

    def increment(self):
        self.frequency += 1
        self.save()

    def decrement(self):
        if self.frequency > 0:
            self.frequency -= 1
        else:
            self.frequency = 0
        self.save()

    def __unicode__(self):
        return "%s: %i" % (self.ngram, self.frequency)

    class Meta:
        verbose_name = "N-Gram Model"
        verbose_name_plural = "N-Gram Models"
        unique_together = ("ngram_id", "analysis")

class NGramPlotAnalysis(models.Model):
    """
    An N-Gram model of a particular plot in the Movies database.
    """

    movie      = models.OneToOneField( 'movies.Movie', related_name="ngram_analysis", null=False )

    @property
    def unigrams(self):
        unigram_type = NGRAM_TYPE_MAP[UNIGRAM]
        return self.filter_by_type(unigram_type).order_by('frequency')

    @property
    def unigram_count(self):
        return self.count(UNIGRAM)

    @property
    def unigram_total(self):
        return self.total(UNIGRAM)

    @property
    def bigrams(self):
        bigram_type = NGRAM_TYPE_MAP[BIGRAM]
        return self.filter_by_type(bigram_type).order_by('frequency')

    @property
    def bigram_count(self):
        return self.count(BIGRAM)

    @property
    def bigram_total(self):
        return self.total(BIGRAM)

    @property
    def trigrams(self):
        trigram_type = NGRAM_TYPE_MAP[TRIGRAM]
        return self.filter_by_type(trigram_type).order_by('frequency')

    @property
    def trigram_count(self):
        return self.count(TRIGRAM)

    @property
    def trigram_total(self):
        return self.total(TRIGRAM)

    def get_ngram_type(self, ngram_type):

        if isinstance(ngram_type, basestring):
            if ngram_type not in NGRAM_TYPE_MAP:
                raise TypeError('"%s" is not a valid N-Gram type.' % ngram_type)
            ngram_type = NGRAM_TYPE_MAP[ngram_type]

        if NGram not in ngram_type.__bases__:
            raise TypeError('NGram types must subclass Ngram, "%s" does not.' % repr(ngram_type))

        return ContentType.objects.get_for_model(ngram_type)

    def filter_by_type(self, ngram_type):
        ngram_type = self.get_ngram_type(ngram_type)
        return self.ngram_model.filter(ngram_type=ngram_type)

    def count(self, ngram_type=UNIGRAM):
        return self.filter_by_type(ngram_type).count()

    def total(self, ngram_type=UNIGRAM):
        count = 0
        for row in self.filter_by_type(ngram_type).values('frequency'):
            count += row['frequency']
        return count

    def average(self, ngram_type=UNIGRAM):
        return float(self.total(ngram_type)) / float(self.count(ngram_type))

    def __unicode__(self):
        return "Analysis for %s" % self.movie.title

    class Meta:
        db_table = "plot_ngram_model"
        verbose_name = "Plot Analysis"
        verbose_name_plural = "Plot Analyses"