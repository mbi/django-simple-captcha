import datetime
import random
import time
import hashlib

from django.utils.encoding import smart_text

from ..models import CaptchaStore
from ..helpers import get_safe_now
from ..conf import settings as captcha_settings


# Heavily based on session key generation in Django
# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
MAX_RANDOM_KEY = 18446744073709551616     # 2 << 63


class BaseStorage(object):
    model_class = CaptchaStore

    def __init__(self, params):
        self.params = params

    def create_obj(self, challenge, response, hashkey, expiration):
        raise NotImplemented("Override this method in %s" % self.__class__.__name__)

    def delete(self, hashkey, obj=None):
        raise NotImplemented("Override this method in %s" % self.__class__.__name__)

    def create(self, challenge, response, hashkey=None, expiration=None):
        response = response.lower()
        hashkey = hashkey or self.get_hashkey(challenge, response)
        expiration = expiration or self.get_expiration()
        return self.create_obj(challenge, response, hashkey, expiration)

    def get(self, hashkey):
        raise NotImplemented("Override this method in %s" % self.__class__.__name__)

    def delete_wanted(self, hashkey, response, date_to_compare=None):
        date_to_compare = date_to_compare or get_safe_now()
        obj = self.get(hashkey)
        if obj.response != response or obj.expiration <= date_to_compare:
            raise self.model_class.DoesNotExist
        self.delete(hashkey, obj=obj)

    def get_hashkey(self, challenge, response):
        key_ = (
            smart_text(randrange(0, MAX_RANDOM_KEY)) +
            smart_text(time.time()) +
            smart_text(challenge, errors='ignore') +
            smart_text(response, errors='ignore')
        ).encode('utf8')
        return hashlib.sha1(key_).hexdigest()

    def get_expiration(self):
        return get_safe_now() + datetime.timedelta(minutes=int(captcha_settings.CAPTCHA_TIMEOUT))

    def remove_expired(self):
        raise NotImplemented("Override this method in %s" % self.__class__.__name__)

    def get_count_of_expired(self):
        raise NotImplemented("Override this method in %s" % self.__class__.__name__)

    def generate_key(self):
        challenge, response = captcha_settings.get_challenge()()
        hashkey = self.get_hashkey(challenge, response)
        self.create(challenge=challenge, response=response, hashkey=hashkey)

        return hashkey
