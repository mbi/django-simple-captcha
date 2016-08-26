from django import forms
from captcha.fields import CaptchaField
from django.http import HttpResponse
from django.contrib.auth.models import User
from six import u
import django

try:
    from django.template import engines, RequestContext
    __is_18 = True
except ImportError:
    from django.template import RequestContext, loader
    __is_18 = False


TEST_TEMPLATE = r'''
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


def _get_template(template_string):
    if __is_18:
        return engines['django'].from_string(template_string)
    else:
        return loader.get_template_from_string(template_string)


def _test(request, form_class):
    passed = False
    if request.POST:
        form = form_class(request.POST)
        if form.is_valid():
            passed = True
    else:
        form = form_class()

    t = _get_template(TEST_TEMPLATE)

    if django.VERSION >= (1, 9):
        return HttpResponse(
            t.render(context=dict(passed=passed, form=form), request=request))
    else:
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


def test_custom_generator(request):
    class CaptchaTestModelForm(forms.ModelForm):
        subject = forms.CharField(max_length=100)
        sender = forms.EmailField()
        captcha = CaptchaField(generator=lambda: ('111111', '111111'))

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
                u(
                    '%(image)s testPerFieldCustomFormatString '
                    '%(hidden_field)s %(text_field)s'
                )
            )
        )
    return _test(request, CaptchaTestFormatForm)


def test_non_required(request):
    class CaptchaTestForm(forms.Form):
        sender = forms.EmailField()
        subject = forms.CharField(max_length=100)
        captcha = CaptchaField(help_text='asdasd', required=False)
    return _test(request, CaptchaTestForm)


def test_id_prefix(request):
    class CaptchaTestForm(forms.Form):
        sender = forms.EmailField()
        subject = forms.CharField(max_length=100)
        captcha1 = CaptchaField(id_prefix="form1")
        captcha2 = CaptchaField(id_prefix="form2")
    return _test(request, CaptchaTestForm)
