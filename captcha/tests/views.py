from django import forms
from captcha.fields import CaptchaField
from django.template import Context, RequestContext, loader
from django.http import HttpResponse


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
        <form action="{% url captcha-test %}" method="post">
            {{form.as_p}}
            <p><input type="submit" value="Continue &rarr;"></p>
        </form>
    </body>
</html>
'''

def test(request):
    
    class CaptchaTestForm(forms.Form):
        subject = forms.CharField(max_length=100)
        sender = forms.EmailField()
        captcha = CaptchaField(help_text='asdasd')
    
    if request.POST:
        form = CaptchaTestForm(request.POST)
        if form.is_valid():
            passed = True
    else:
        form = CaptchaTestForm()
        
    t = loader.get_template_from_string(TEST_TEMPLATE)
    return HttpResponse(t.render(RequestContext(request, locals())))


def test_custom_error_message(request):

    class CaptchaTestForm(forms.Form):
        captcha = CaptchaField(help_text='asdasd', error_messages=dict(invalid='TEST CUSTOM ERROR MESSAGE'))

    if request.POST:
        form = CaptchaTestForm(request.POST)
        if form.is_valid():
            passed = True
    else:
        form = CaptchaTestForm()

    t = loader.get_template_from_string(TEST_TEMPLATE)
    return HttpResponse(t.render(RequestContext(request, locals())))



def test_per_form_format(request):
    
    class CaptchaTestForm(forms.Form):
        captcha = CaptchaField(help_text='asdasd', error_messages=dict(invalid='TEST CUSTOM ERROR MESSAGE'), \
            output_format=u'%(image)s testPerFieldCustomFormatString %(hidden_field)s %(text_field)s' )

    if request.POST:
        form = CaptchaTestForm(request.POST)
        if form.is_valid():
            passed = True
    else:
        form = CaptchaTestForm()

    t = loader.get_template_from_string(TEST_TEMPLATE)
    return HttpResponse(t.render(RequestContext(request, locals())))
