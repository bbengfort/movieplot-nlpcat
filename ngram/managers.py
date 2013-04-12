__author__ = 'benjamin'

from django.db import models
from django.core.exceptions import MultipleObjectsReturned

class NGramManager(models.Manager):

    def get_by_natural_key(self, *args):

        # Special case for Unigrams
        if len(args) == 1:
            return self.get(token=args[0])

        # For Bigrams through Quadgrams
        keys   = ('alpha', 'beta', 'gamma', 'delta')
        kwargs = dict(zip(keys, args))
        try:
            return self.get(**kwargs)
        except MultipleObjectsReturned:
            raise MultipleObjectsReturned("Did you specify the correct number of tokens for the N-Gram?")