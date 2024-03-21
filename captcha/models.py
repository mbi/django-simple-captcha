import datetime
import hashlib
import logging
import random
import time
from typing import Final

from django.db import models
from django.utils import timezone
from django.utils.encoding import smart_str

from captcha.conf import settings as captcha_settings


# Heavily based on session key generation in Django
# Use the system (hardware-based) random number generator if it exists.
randrange: function = random.SystemRandom().randrange if hasattr(random, "SystemRandom") else random.randrange

MAX_RANDOM_KEY: Final[int] = 18446744073709551616  # 2 << 63

logger: logging.Logger = logging.getLogger(__name__)


class CaptchaStore(models.Model):
    id = models.AutoField(primary_key=True)
    challenge = models.CharField(blank=False, max_length=32)
    response = models.CharField(blank=False, max_length=32)
    hashkey = models.CharField(blank=False, max_length=40, unique=True)
    expiration = models.DateTimeField(blank=False)

    def save(self, *args, **kwargs) -> None:
        self.response: models.CharField = self.response.lower()

        if not self.expiration:
            self.expiration = timezone.now() + datetime.timedelta(
                minutes=int(captcha_settings.CAPTCHA_TIMEOUT)
            )

        if not self.hashkey:
            key_: bytes = (
                smart_str(randrange(0, MAX_RANDOM_KEY))
                + smart_str(time.time())
                + smart_str(self.challenge, errors="ignore")
                + smart_str(self.response, errors="ignore")
            ).encode("utf8")

            self.hashkey: models.CharField = hashlib.sha1(key_).hexdigest()
            del key_

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.challenge

    @classmethod
    def remove_expired(cls) -> None:
        cls.objects.filter(expiration__lte=timezone.now()).delete()

    @classmethod
    def generate_key(cls, generator=None) -> str:
        challenge, response = captcha_settings.get_challenge(generator)()
        store = cls.objects.create(challenge=challenge, response=response)

        return store.hashkey

    @classmethod
    def pick(cls) -> str:
        if not captcha_settings.CAPTCHA_GET_FROM_POOL:
            return cls.generate_key()

        def fallback():
            logger.error("Couldn't get a captcha from pool, generating")
            return cls.generate_key()

        # Pick up a random item from pool
        minimum_expiration = timezone.now() + datetime.timedelta(
            minutes=int(captcha_settings.CAPTCHA_GET_FROM_POOL_TIMEOUT)
        )
        store = (
            cls.objects.filter(expiration__gt=minimum_expiration).order_by("?").first()
        )

        return (store and store.hashkey) or fallback()

    @classmethod
    def create_pool(cls, count: int=1000):
        assert count > 0
        while count > 0:
            cls.generate_key()
            count -= 1
