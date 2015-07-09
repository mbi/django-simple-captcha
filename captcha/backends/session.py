from .base import BaseStore
from captcha.conf import settings as captcha_settings
from django.conf import settings
import django
try:
    from importlib import import_module
    Store = import_module(settings.SESSION_ENGINE).SessionStore
except:
    # py 2.6
    backend = __import__(settings.SESSION_ENGINE, globals(), locals(), ['SessionStore'], -1)
    Store = backend.SessionStore


class SessionStore(BaseStore):

    def generate_key(self):
        challenge, response = super(SessionStore, self).generate_key()
        store = Store()
        store.set_expiry(60 * int(captcha_settings.CAPTCHA_TIMEOUT))
        store['challenge'] = challenge
        store['response'] = response
        store.save()
        return store.session_key

    def remove_expired(self):
        if not django.get_version() < '1.5':
            Store.clear_expired()

    def get(self, response=None, hashkey=None, allow_expired=True):
        s = Store(session_key=hashkey)
        if not s.get('response'):
            raise self.DoesNotExist
        if response:
            if s['response'] != response:
                raise self.DoesNotExist
            if not allow_expired and s.get_expiry_age() < 0:
                raise self.DoesNotExist
        return s
