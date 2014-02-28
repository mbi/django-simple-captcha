from django import forms
from captcha.fields import CaptchaField
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.contrib.auth.models import User


TEST_TEMPLATE = r'''
{% load url from future %}
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
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
'''

def _test(request, form_class):
    passed = False
    if request.POST:
        form = form_class(request.POST)
        if form.is_valid():
            passed = True
    else:
        form = form_class()

    t = loader.get_template_from_string(TEST_TEMPLATE)
    return HttpResponse(
        t.render(RequestContext(request, dict(passed=passed, form=form))))


def test(request):
    class CaptchaTestForm(forms.Form):
        subject = forms.CharField(max_length=100)
        sender = forms.EmailField()
        captcha = CaptchaField(help_text='asdasd')
    return _test(request, CaptchaTestForm)


def test_model_form(request):
    class CaptchaTestModelForm(forms.ModelForm):
        subject = forms.CharField(max_length=100)
        sender = forms.EmailField()
        captcha = CaptchaField(help_text='asdasd')

        class Meta:
            model = User
            fields = ('subject', 'sender', 'captcha', )

    return _test(request, CaptchaTestModelForm)


def test_custom_error_message(request):
    class CaptchaTestErrorMessageForm(forms.Form):
        captcha = CaptchaField(
            help_text='asdasd',
            error_messages=dict(invalid='TEST CUSTOM ERROR MESSAGE')
        )
    return _test(request, CaptchaTestErrorMessageForm)


def test_per_form_format(request):
    class CaptchaTestFormatForm(forms.Form):
        captcha = CaptchaField(
            help_text='asdasd',
            error_messages=dict(invalid='TEST CUSTOM ERROR MESSAGE'),
            output_format=(
                '%(image)s testPerFieldCustomFormatString '
                '%(hidden_field)s %(text_field)s'
            )
        )
    return _test(request, CaptchaTestFormatForm)


def test_non_required(request):
    class CaptchaTestForm(forms.Form):
        sender = forms.EmailField()
        subject = forms.CharField(max_length=100)
        captcha = CaptchaField(help_text='asdasd', required=False)
    return _test(request, CaptchaTestForm)
