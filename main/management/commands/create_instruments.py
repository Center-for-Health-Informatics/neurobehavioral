from django.core.management.base import BaseCommand, CommandError

from main.instrument_management import create_instruments_for_all_incomplete

class Command(BaseCommand):
    # provide some help text
    help = "creates instruments for any visits that haven't been processed yet"

    # add optional command line arguments
    def add_arguments(self, parser):
        pass

    # this will be executed when the command is called
    def handle(self, *args, **options):
        self.stdout.write('### Starting instrument creation ####################')
        response = create_instruments_for_all_incomplete()
        for error in response:
            self.stdout.write(error)
        self.stdout.write('### Instrument creation complete ####################')
