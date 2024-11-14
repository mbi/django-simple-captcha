from rest_framework import serializers
from rest_framework.fields import empty

from captcha.validators import captcha_validate


class CaptchaSerializer(serializers.Serializer):
    """Serializer captcha code and captcha hashkey"""

    captcha_code = serializers.CharField(max_length=32, write_only=True, required=True)
    captcha_hashkey = serializers.CharField(
        max_length=40, write_only=True, required=True
    )

    def run_validation(self, data=empty):
        values = super().run_validation(data=data)
        captcha_validate(values["captcha_hashkey"], values["captcha_code"])
        return values


class CaptchaModelSerializer(serializers.ModelSerializer):
    """Model serializer captcha code and captcha hashkey"""

    captcha_code = serializers.CharField(max_length=32, write_only=True, required=True)
    captcha_hashkey = serializers.CharField(
        max_length=40, write_only=True, required=True
    )

    def run_validation(self, data=empty):
        values = super().run_validation(data=data)
        captcha_validate(values["captcha_hashkey"], values["captcha_code"])
        return values
