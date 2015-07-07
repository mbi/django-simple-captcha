from captcha.conf import settings as captcha_settings
from ..models import CaptchaStore, get_safe_now
from .base import BaseStore

class DBStore(BaseStore):
    def __init__(self, key = None):
        self._captcha = {}
        if key:
            try:
                cap = CaptchaStore.objects.get(hashkey = key)
                self._captcha = {
                    'hashkey': cap.hashkey,
                    'challenge': cap.challenge,
                    'response': cap.response,
                    'expiration': cap.expiration,
                }
            except CaptchaStore.DoesNotExist:
                raise self.DoesNotExist
        
    def __getitem__(self, key):
        return self._captcha[key]
        
    def remove_expired(self):
        CaptchaStore.objects.filter(expiration__lte=get_safe_now()).delete()

    def generate_key(self):
        return CaptchaStore.generate_key()

    def get(self, response=None, hashkey=None, allow_expired = True):
        store = DBStore(hashkey)
        if response and store['response'] != response:
            raise self.DoesNotExist
        if not allow_expired and store['expiration'] < get_safe_now():
            raise self.DoesNotExist
        return store
        
    def delete(self):
        CaptchaStore.objects.filter(hashkey = self['hashkey']).delete()
