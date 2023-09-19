from django import forms

from captcha.fields import CaptchaField, CaptchaTextInput


class CustomCaptchaTextInput(CaptchaTextInput):
    template_name = "captcha_test/custom_captcha_field.html"


class CaptchaForm(forms.Form):
    captcha = CaptchaField()


class CustomCaptchaForm(forms.Form):
    captcha = CaptchaField(widget=CustomCaptchaTextInput)
