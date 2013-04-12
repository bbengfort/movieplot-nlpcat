__author__ = 'benjamin'

from django.db import models
from movieplot.core.utils import remove_punctuation

class MovieManager(models.Manager):

    def search(self, title, **filters):

        # Don't return anything on empty search
        if not title and not filters:
            return self.none()
        queryset = self.all()

        # Allow for None
        title = title or ''

        # Remove punctuation
        title = remove_punctuation(title)

        # Filter on all keywords
        stopwords = ("the", "a", "an", "of", "at", "on", "to", "over", "and", "but", "or", "nor")
        for keyword in title.split():
            keyword = keyword.strip()
            if keyword.lower() in stopwords: continue
            queryset = queryset.filter(title__icontains=keyword)

        if filters:
            # TODO: implement other filters
            pass

        return queryset

    def random(self):
        """
        Returns a random movie with a plot.
        """
        return self.exclude(plot__isnull=True).order_by('?')[0]