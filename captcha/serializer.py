from captcha.conf import settings
from captcha.models import CaptchaStore

from django.utils import timezone
if django.VERSION >= (3, 0):
    from django.utils.translation import gettext_lazy as ugettext_lazy
else:
    from django.utils.translation import ugettext_lazy

from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.fields import empty

''' 
Support for rest_framework 
    Use CaptchaSerializer replace Serializer,
    Use CaptchaModelSerializer replace ModelSerializer
'''

def captcha_validation(hashkey, code):
    if not settings.CAPTCHA_GET_FROM_POOL:
        CaptchaStore.remove_expired()
    if settings.CAPTCHA_TEST_MODE and code == 'passed':
        try:
            CaptchaStore.objects.get(hashkey=hashkey).delete()
        except CaptchaStore.DoesNotExist:
            pass
    else:
        try:
            CaptchaStore.objects.get(response=code, hashkey=hashkey, expiration__gt=timezone.now()).delete()
        except CaptchaStore.DoesNotExist:
            errors={}
            errors['captcha'] = [ugettext_lazy("Invalid CAPTCHA")]
            raise ValidationError(errors)


class CaptchaSerializer(serializers.Serializer):

    captcha_hashkey = serializers.CharField(max_length=40, write_only=True, required=True)
    captcha_code = serializers.CharField(max_length=32, write_only=True, required=True)

    def run_validation(self, data=empty):
        values = super().run_validation(data=data)
        code, hashkey= values['captcha_code'].lower(), values['captcha_hashkey'].lower()
        captcha_validation(hashkey, code)
        return values


class CaptchaModelSerializer(serializers.ModelSerializer):

    captcha_hashkey = serializers.CharField(max_length=40, write_only=True, required=True)
    captcha_code = serializers.CharField(max_length=32, write_only=True, required=True)

    def run_validation(self, data=empty):
        values = super().run_validation(data=data)
        code, hashkey= values['captcha_code'].lower(), values['captcha_hashkey'].lower()
        captcha_validation(hashkey, code)
        return values
        