import sys

from django.core.management.base import BaseCommand

from captcha.storages import storage


class Command(BaseCommand):
    help = "Clean up expired captcha hashkeys."

    def handle(self, **options):
        verbose = int(options.get('verbosity'))
        expired_keys = storage.get_count_of_expired()
        if verbose >= 1:
            print("Currently %d expired hashkeys" % expired_keys)
        try:
            storage.remove_expired()
        except:
            if verbose >= 1:
                print("Unable to delete expired hashkeys.")
            sys.exit(1)
        if verbose >= 1:
            if expired_keys > 0:
                print("%d expired hashkeys removed." % expired_keys)
            else:
                print("No keys to remove.")
