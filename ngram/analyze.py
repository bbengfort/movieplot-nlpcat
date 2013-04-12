__author__ = 'benjamin'

import nltk
from ngram.models import *
from movies.models import *
from movieplot.core.counting import Histogram

class TextProcessor(object):
    """
    Takes a generic bit of unstructured text that has not been processed,
    and is of a length that is manageable in memory, then segments,
    tokenizes, and tags the text. (It does not deal with paragraphs).

    @todo: Add Parsing!
    """

    def segment(self, text):
        """
        Override to specify a different segmenter. Default NLTK used now.
        """
        if not text: return []
        return nltk.sent_tokenize(text)

    def tokenize(self, text):
        """
        Override to specify a different tokenizer. Default NLTK used now.
        """
        if not text: return []
        return nltk.word_tokenize(text)

    def postag(self, tokens):
        """
        Override to specify a different tagger. Default NLTK used now.
        """
        if not tokens: return []
        return nltk.pos_tag(tokens)

    def process(self, text):
        """
        Returns a list of sentences where each sentence is a list of pos
        tagged token tuples, where the first part of the tuple is the
        token and the second part is the part of speech.
        """
        for sentence in self.segment(text):
            yield self.postag(self.tokenize(sentence))

    def serialize(self, text, preprocessed=False):
        """
        Creates a representation that can be saved to the database.

        Choices: JSON, Brown Simple Tags, Treebanking
        """
        pass

    def deserialize(self, text):
        """
        Unpacks a saved representation of the preprocessed text.
        """
        pass

class NGramAnalyzer(object):
    """
    Takes a generic bit of text and outputs NGrams along with their
    associated frequencies.
    """

    # Static Processor to reduce load times in memory
    processor = TextProcessor()

    def __init__(self, text, N=1, preprocessed=False):
        self.N = N
        self.text = text
        self._frequency = Histogram()
        self.preprocessed = preprocessed

    @property
    def frequency(self):
        if not self._frequency:
            for ngram in self:
                self._frequency.increment(ngram)
        return self._frequency

    def tokenize(self):
        """
        Tokenize using processor.
        """
        if not self.preprocessed:
            text = self.processor.process(self.text)
        else:
            text = self.processor.deserialize(self.text)

        for sentence in text:
            for token, postag in sentence:
                yield token.lower()

    def __iter__(self):
        if self.N == 1:
            # Special case for Unigrams
            for token in self.tokenize(): yield token
        else:
            ngram = []
            for token in self.tokenize():
                if len(ngram) < self.N:
                    ngram.append(token)
                if len(ngram) == self.N:
                    yield tuple(ngram)
                    ngram = ngram[1:]

    def __len__(self):
        return self.frequency.total

class NGramModelAnalyzer(NGramAnalyzer):
    """
    An NGram analyzer that interacts with the database.

    @note: __iter__ won't save anything to the database, use ngrams() if
    you want to create new ngrams in the course of the analysis.
    """
    model_map = {
        1: Unigram,
        2: Bigram,
        3: Trigram,
    }

    def __init__(self, *args, **kwargs):
        super(NGramModelAnalyzer, self).__init__(*args, **kwargs)
        self.model = self.model_map[self.N]

    @property
    def frequency(self):
        if not self._frequency:
            for ngram in self.ngrams():
                self._frequency.increment(ngram)
        return self._frequency

    def tokenize(self, save=True):
        """
        Spits out tokens as Unigrams.

        If save is true, will add rows to the database, otherwise errors
        will occur if the Unigram does not exist in the database.
        """
        for token in super(NGramModelAnalyzer, self).tokenize():
            if save:
                yield Unigram.objects.get_or_create(token=token)[0]
            else:
                yield Unigram.objects.get_by_natural_key(token)

    def ngrams(self, save=True):
        if self.N == 1:
            # Special case for Unigrams
            for token in self.tokenize(save=save): yield token
        else:
            ngram = []
            for token in self.tokenize(save=save):
                if len(ngram) < self.N:
                    ngram.append(token)
                if len(ngram) == self.N:
                    keys   = ('alpha', 'beta', 'gamma', 'delta')
                    kwargs = dict(zip(keys, ngram))
                    if save:
                        yield self.model.objects.get_or_create(**kwargs)[0]
                    else:
                        yield self.model.objects.get(**kwargs)
                    ngram = ngram[1:]

    def __iter__(self):
        try:
            for ngram in self.ngrams(save=False):
                yield ngram
        except (self.model.DoesNotExist, Unigram.DoesNotExist) as e:
            raise self.model.DoesNotExist("__iter__ does not save to the database, use ngrams() to create new ngrams.")

class MultiNGramAnalyzer(NGramAnalyzer):
    """
    Same interface as the NGramAnalyzer but yields multiple NGrams up to
    the N specified in the init, which makes for a fairly confusing group
    of yielded N-Grams, but also very quickly gets all the NGrams out of
    the piece of text for analysis.
    """

    def __iter__(self):

        if self.N == 1:
            # Special case for Unigrams
            for token in self.tokenize(): yield token
        else:
            state = []
            for token in self.tokenize():
                if len(state) < self.N:
                    state.append(token)
                if len(state) == self.N:
                    ngram = []
                    for t in state:
                        ngram.append(t)
                        yield tuple(ngram)
                    state = state[1:]

class MultiNGramModelAnalyzer(NGramModelAnalyzer):
    """
    An MultiNGramAnalyzer that uses the database.
    """

    def ngrams(self, save=True):
        if self.N == 1:
            # Special case for Unigrams (Which have been fetched by tokenize())
            for token in self.tokenize(save=save): yield token
        else:
            state = []
            for token in self.tokenize(save=save):
                if len(state) < self.N:
                    state.append(token)
                if len(state) == self.N:
                    ngram = []
                    for t in state:
                        ngram.append(t)

                        if len(ngram) == 1:
                            yield ngram[0]
                            continue

                        keys   = ('alpha', 'beta', 'gamma', 'delta')
                        kwargs = dict(zip(keys, ngram))
                        self.model = self.model_map[len(ngram)]
                        if save:
                            yield self.model.objects.get_or_create(**kwargs)[0]
                        else:
                            yield self.model.objects.get(**kwargs)
                    state = state[1:]

class MoviePlotAnalyzer(object):
    """
    Utilizes a MultiNGramModelAnalyzer to create Plot Analyses in the
    database -- this is only here because of the current coupling between
    the ngram app and the movies app.
    """

    max_n_value = 3

    @classmethod
    def analyze(cls, movie):
        if not isinstance(movie, Movie):
            raise TypeError("Only movies can be analyzed.")

        analyzer  = MultiNGramModelAnalyzer(movie.plot, cls.max_n_value, preprocessed=False)
        histogram = analyzer.frequency
        analysis  = NGramPlotAnalysis.objects.create(movie=movie)

        for ngram, count in histogram.items():
            NGramModel.objects.create(analysis=analysis, ngram=ngram, frequency=count)

        return analysis

def ngram_factory(text, N, **kwargs):
    database = kwargs.pop('database', False)
    if database:
        return NGramModelAnalyzer(text, N, **kwargs)
    else:
        return NGramAnalyzer(text, N, **kwargs)

def unigrams(text, **kwargs):
    return ngram_factory(text, 1, **kwargs)

def bigrams(text, **kwargs):
    return ngram_factory(text, 2, **kwargs)

def trigrams(text, **kwargs):
    return ngram_factory(text, 3, **kwargs)