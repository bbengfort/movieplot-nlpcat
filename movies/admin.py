from django.contrib import admin
from movies.models import *

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Director)
admin.site.register(Writer)
admin.site.register(Actor)