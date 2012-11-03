Using django-simple-captcha
===========================

Installation
+++++++++++++

1. Download ``django-simple-captcha`` using pip_ by running: ``pip install  django-simple-captcha``
2. Add ``captcha`` to the ``INSTALLED_APPS`` in your ``settings.py``
3. Run ``python manage.py syncdb`` (or ``python manage.py migrate`` if you are managing databae migrations via South) to create the required database tables
4. Add an entry to your ``urls.py``::

        urlpatterns += patterns('',
            url(r'^captcha/', include('captcha.urls')),
        )


.. _pip: http://pypi.python.org/pypi/pip

Adding to a Form
+++++++++++++++++

Using a ``CaptchaField`` is quite straight-forward:

Define the Form
----------------


To embed a CAPTCHA in your forms, simply add a ``CaptchaField`` to the form definition::

    from django import forms
    from captcha.fields import CaptchaField

    class CaptchaTestForm(forms.Form):
        myfield = AnyOtherField()
        captcha = CaptchaField()

…or, as a ``ModelForm``::


    from django import forms
    from captcha.fields import CaptchaField

    class CaptchaTestModelForm(forms.ModelForm):
        captcha = CaptchaField()
        class Meta:
            model = MyModel

Validate the Form
-----------------

In your view, validate the form as usually: if the user didn't provide a valid response to the CAPTCHA challenge, the form will raise a ``ValidationError``::

    def some_view(request):
        if request.POST:
            form = CaptchaTestForm(request.POST)

            # Validate the form: the captcha field will automatically
            # check the input
            if form.is_valid():
                human = True
        else:
            form = CaptchaTestForm()

        return render_to_response('template.html',locals())

Example usage for ajax form
---------------------------
from django.views.generic.edit import CreateView
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import HttpResponse
import json

class AjaxExampleForm(CreateView):
    template_name = ''
    form_class = AjaxForm

    def form_invalid(self, form):
        if self.request.is_ajax():
            to_json_responce = dict()
            to_json_responce['status'] = 0
            to_json_responce['form_errors'] = form.errors

            to_json_responce['new_cptch_key'] = CaptchaStore.generate_key()
            to_json_responce['new_cptch_image'] = captcha_image_url(to_json_responce['new_cptch_key'])

            return HttpResponse(json.dumps(to_json_responce), mimetype='application/json')

    def form_valid(self, form):
        form.save()
        if self.request.is_ajax():
            to_json_responce = dict()
            to_json_responce['status'] = 1

            to_json_responce['new_cptch_key'] = CaptchaStore.generate_key()
            to_json_responce['new_cptch_image'] = captcha_image_url(to_json_responce['new_cptch_key'])

            return HttpResponse(json.dumps(to_json_responce), mimetype='application/json')

And in javascript your must update image and hidden input in form

Example usage ajax refresh button
---------------------------------

# html
    <form action='.' method='POST'>
        {{ form }}
        <input type="submit" />
        <button class='js-captcha-refresh'></button>
    </form>

# javascript
    $('.js-captcha-refresh').click(function(){
        $form = $(this).parents('form');

        $.getJSON($(this).data('url'), {}, function(json) {
            // This your should update captcha image src and captcha hidden input
        });

        return false;
    });
