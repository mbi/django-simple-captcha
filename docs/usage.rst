Using django-simple-captcha
===========================

Installation
+++++++++++++

1. Install ``django-simple-captcha`` via pip_: ``pip install  django-simple-captcha``
2. Add ``captcha`` to the ``INSTALLED_APPS`` in your ``settings.py``
3. Run ``python manage.py migrate``
4. Add an entry to your ``urls.py``::

        urlpatterns += [
            url(r'^captcha/', include('captcha.urls')),
        ]

.. _pip: http://pypi.python.org/pypi/pip


Note: PIL and Pillow require that image libraries are installed on your system. On e.g. Debian or Ubuntu, you'd need these packages to compile and install Pillow::

       apt-get -y install libz-dev libjpeg-dev libfreetype6-dev python-dev

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

In your view, validate the form as usual. If the user didn't provide a valid response to the CAPTCHA challenge, the form will raise a ``ValidationError``::

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

Passing arguments to the field
------------------------------

``CaptchaField`` takes a few optional arguements:

* ``output_format`` will let you format the layout of the rendered field. Defaults to the value defined in : :ref:`output_format_ref`.
* ``id_prefix`` Optional prefix that will be added to the ID attribute in the generated fields and labels, to be used when e.g. several Captcha fields are being displayed on a same page. (added in version 0.4.4)
* ``generator`` Optional callable or module path to callable that will be used to generate the challenge and the response, e.g. ``generator='path.to.generator_function'`` or ``generator=lambda: ('LOL', 'LOL')``, see also :ref:`generators_ref`. Defaults to whatever is defined in ``settings.CAPTCHA_CHALLENGE_FUNCT``.

Example usage for ajax form
---------------------------

An example CAPTCHA validation in AJAX::

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
                to_json_response = dict()
                to_json_response['status'] = 0
                to_json_response['form_errors'] = form.errors

                to_json_response['new_cptch_key'] = CaptchaStore.generate_key()
                to_json_response['new_cptch_image'] = captcha_image_url(to_json_response['new_cptch_key'])

                return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        def form_valid(self, form):
            form.save()
            if self.request.is_ajax():
                to_json_response = dict()
                to_json_response['status'] = 1

                to_json_response['new_cptch_key'] = CaptchaStore.generate_key()
                to_json_response['new_cptch_image'] = captcha_image_url(to_json_response['new_cptch_key'])

                return HttpResponse(json.dumps(to_json_response), content_type='application/json')


And in javascript your must update the image and hidden input in form


Example usage ajax refresh button
---------------------------------

# html::

    <form action='.' method='POST'>
        {{ form }}
        <input type="submit" />
        <button class='js-captcha-refresh'></button>
    </form>

# javascript::

    $('.js-captcha-refresh').click(function(){
        $form = $(this).parents('form');

        $.getJSON($(this).data('url'), {}, function(json) {
            // This should update your captcha image src and captcha hidden input
        });

        return false;
    });
    

Example usage ajax refresh 
---------------------------------

# javascript::

    $('.captcha').click(function () {
        $.getJSON("/captcha/refresh/", function (result) {
            $('.captcha').attr('src', result['image_url']);
            $('#id_captcha_0').val(result['key'])
        });


    });
