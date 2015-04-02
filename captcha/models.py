from captcha.conf import settings as captcha_settings
from django.db import models
from django.conf import settings
from django.utils.encoding import smart_text
import datetime
import random
import time
import hashlib


# Heavily based on session key generation in Django
# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
MAX_RANDOM_KEY = 18446744073709551616     # 2 << 63


def get_safe_now():
    try:
        from django.utils.timezone import utc
        if settings.USE_TZ:
            return datetime.datetime.utcnow().replace(tzinfo=utc)
    except:
        pass
    return datetime.datetime.now()


class CaptchaStore(models.Model):
    challenge = models.CharField(blank=False, max_length=32)
    response = models.CharField(blank=False, max_length=32)
    hashkey = models.CharField(blank=False, max_length=40, unique=True)
    expiration = models.DateTimeField(blank=False)

    def save(self, *args, **kwargs):
        self.response = self.response.lower()
        if not self.expiration:
            self.expiration = get_safe_now() + datetime.timedelta(minutes=int(captcha_settings.CAPTCHA_TIMEOUT))
        if not self.hashkey:
            key_ = (
                smart_text(randrange(0, MAX_RANDOM_KEY)) +
                smart_text(time.time()) +
                smart_text(self.challenge, errors='ignore') +
                smart_text(self.response, errors='ignore')
            ).encode('utf8')
            self.hashkey = hashlib.sha1(key_).hexdigest()
            del(key_)
        super(CaptchaStore, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.challenge

    def remove_expired(cls):
        cls.objects.filter(expiration__lte=get_safe_now()).delete()
    remove_expired = classmethod(remove_expired)

    @classmethod
    def generate_key(cls):
        challenge, response = captcha_settings.get_challenge()()
        store = cls.objects.create(challenge=challenge, response=response)

        return store.hashkey
