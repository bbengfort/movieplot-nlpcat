"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

def save_slugs(model):
    from django.db import connection

    counts = 0
    dups   = []
    for thing in model.objects.all():
        try:
            thing.save()
            counts += 1
        except Exception as e:
            connection._rollback()
            dups.append(thing)
            print e

    return counts, dups
