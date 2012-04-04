from django.core.management.base import BaseCommand, CommandError
import sys

from optparse import make_option

class Command(BaseCommand):
    help = "Clean up expired captcha hashkeys."
    
    def handle(self, **options):
        from captcha.models import CaptchaStore
        import datetime
        verbose = int(options.get('verbosity'))
        expired_keys = CaptchaStore.objects.filter(expiration__lte=datetime.datetime.now()).count()
        if verbose >= 1:
            print "Currently %s expired hashkeys" % expired_keys
        try:
            CaptchaStore.remove_expired()
        except:
            if verbose >= 1 :
                print "Unable to delete expired hashkeys."
            sys.exit(1)
        if verbose >= 1:
            if expired_keys > 0:
                print "Expired hashkeys removed."
            else:
                print "No keys to remove."
        
        
