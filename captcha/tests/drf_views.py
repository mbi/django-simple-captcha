from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth.models import User

from captcha.serializers import CaptchaModelSerializer, CaptchaSerializer


@api_view(["POST"])
def test_serializer(request):
    serializer = CaptchaSerializer(data=request.POST)
    serializer.is_valid(raise_exception=True)
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def test_model_serializer(request):
    class UserCaptchaModelSerializer(CaptchaModelSerializer):
        subject = serializers.CharField(max_length=100)
        sender = serializers.EmailField()

        class Meta:
            model = User
            fields = ("subject", "sender", "captcha_code", "captcha_hashkey")

    serializer = UserCaptchaModelSerializer(data=request.POST)
    serializer.is_valid(raise_exception=True)
    return Response(status=status.HTTP_200_OK)
