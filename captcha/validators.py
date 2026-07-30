from rest_framework import exceptions

from django.utils import timezone
from django.utils.translation import gettext_lazy as gettext_lazy

from captcha.conf import settings
from captcha.models import CaptchaStore


def captcha_validate(hashkey, response):
    hashkey, response = hashkey.lower(), response.lower()

    if not settings.CAPTCHA_GET_FROM_POOL:
        CaptchaStore.remove_expired()
    if settings.CAPTCHA_TEST_MODE and response.lower() == "passed":
        try:
            CaptchaStore.objects.get(hashkey=hashkey).delete()
        except CaptchaStore.DoesNotExist:
            pass
    else:
        store = CaptchaStore.objects.filter(
            hashkey=hashkey, expiration__gt=timezone.now()
        ).first()
        # A captcha can only be attempted once: invalidate the store
        # even when the response is wrong, to prevent brute-force attacks.
        if store is not None:
            store.delete()
        if store is None or store.response != response:
            raise exceptions.ValidationError({"error": gettext_lazy("Invalid CAPTCHA")})
