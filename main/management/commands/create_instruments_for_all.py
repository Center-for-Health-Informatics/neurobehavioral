from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    # provide some help text
    help = "creates instruments for any visits that haven't been processed yet"

    # add optional command line arguments
    def add_arguments(self, parser):
        pass

    # this will be executed when the command is called
    def handle(self, *args, **options):
        self.stdout.write('hello world')