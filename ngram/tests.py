"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.db import connection
from django.test import TestCase
from ngram.models import *

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

def create_or_get_test_data():
    sentence = ['The', 'brown', 'bear', 'ate', 'some', 'bad', 'berries', '.']
    ngrams = {
        'unigrams' : [],
        'bigrams'  : [],
        'trigrams' : [],
    }

    for token in sentence:
        try:
            ngrams['unigrams'].append(Unigram.objects.create(token=token))
        except:
            connection._rollback()
            ngrams['unigrams'].append(Unigram.objects.get_by_natural_key(token))

    bigram = []
    for unigram in ngrams['unigrams']:
        if len(bigram) < 2:
            bigram.append(unigram)
        if len(bigram) == 2:
            try:
                ngrams['bigrams'].append(Bigram.objects.create(alpha=bigram[0], beta=bigram[1]))
            except:
                connection._rollback()
                ngrams['bigrams'].append(Bigram.objects.get_by_natural_key(*bigram))
            bigram = bigram[1:]

    trigram = []
    for unigram in ngrams['unigrams']:
        if len(trigram) < 3:
            trigram.append(unigram)
        if len(trigram) == 3:
            try:
                ngrams['trigrams'].append(Trigram.objects.create(alpha=trigram[0], beta=trigram[1], gamma=trigram[2]))
            except:
                connection._rollback()
                ngrams['trigrams'].append(Trigram.objects.get_by_natural_key(*trigram))
            trigram = trigram[1:]

    return ngrams
