from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django import forms
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import engines

from captcha.fields import CaptchaField
from captcha.serializers import CaptchaModelSerializer, CaptchaSerializer


TEST_TEMPLATE = r"""
<!doctype html>
<html>
    <head>
        <meta http-equiv="Content-type" content="text/html; charset=utf-8">
        <title>captcha test</title>
    </head>
    <body>
        {% if passed %}
        <p style="color:green">Form validated</p>
        {% endif %}
        {% if form.errors %}
        {{form.errors}}
        {% endif %}

        <form action="{% url 'captcha-test' %}" method="post">
            {{form.as_p}}
            <p><input type="submit" value="Continue &rarr;"></p>
        </form>
    </body>
</html>
"""


def _get_template(template_string):
    return engines["django"].from_string(template_string)


def _test(request, form_class):
    passed = False
    if request.POST:
        form = form_class(request.POST)
        if form.is_valid():
            passed = True
    else:
        form = form_class()

    t = _get_template(TEST_TEMPLATE)

    return HttpResponse(
        t.render(context=dict(passed=passed, form=form), request=request)
    )


def test(request):
    class CaptchaTestForm(forms.Form):
        subject = forms.CharField(max_length=100)
        sender = forms.EmailField()
        captcha = CaptchaField(help_text="asdasd")

    return _test(request, CaptchaTestForm)


def test_model_form(request):
    class CaptchaTestModelForm(forms.ModelForm):
        subject = forms.CharField(max_length=100)
        sender = forms.EmailField()
        captcha = CaptchaField(help_text="asdasd")

        class Meta:
            model = User
            fields = ("subject", "sender", "captcha")

    return _test(request, CaptchaTestModelForm)


def test_custom_generator(request):
    class CaptchaTestModelForm(forms.ModelForm):
        subject = forms.CharField(max_length=100)
        sender = forms.EmailField()
        captcha = CaptchaField(generator=lambda: ("111111", "111111"))

        class Meta:
            model = User
            fields = ("subject", "sender", "captcha")

    return _test(request, CaptchaTestModelForm)


def test_custom_error_message(request):
    class CaptchaTestErrorMessageForm(forms.Form):
        captcha = CaptchaField(
            help_text="asdasd", error_messages=dict(invalid="TEST CUSTOM ERROR MESSAGE")
        )

    return _test(request, CaptchaTestErrorMessageForm)


def test_non_required(request):
    class CaptchaTestForm(forms.Form):
        sender = forms.EmailField()
        subject = forms.CharField(max_length=100)
        captcha = CaptchaField(help_text="asdasd", required=False)

    return _test(request, CaptchaTestForm)


def test_id_prefix(request):
    class CaptchaTestForm(forms.Form):
        sender = forms.EmailField()
        subject = forms.CharField(max_length=100)
        captcha1 = CaptchaField(id_prefix="form1")
        captcha2 = CaptchaField(id_prefix="form2")

    return _test(request, CaptchaTestForm)


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
