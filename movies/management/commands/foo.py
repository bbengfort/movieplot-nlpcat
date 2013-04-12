from django.core.management import BaseCommand, CommandError

class Command(BaseCommand):
    
    def handle(self, *args, **opts):
        print "Tested!"
