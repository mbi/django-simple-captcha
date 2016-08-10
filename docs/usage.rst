Using django-simple-captcha
===========================

Installation
+++++++++++++

1. Download ``django-simple-captcha`` using pip_ by running: ``pip install  django-simple-captcha``
2. Add ``captcha`` to the ``INSTALLED_APPS`` in your ``settings.py``
3. Run ``python manage.py syncdb`` (or ``python manage.py migrate`` if you are managing database migrations via South) to create the required database tables
4. Add an entry to your ``urls.py``::

        urlpatterns += patterns('',
            url(r'^captcha/', include('captcha.urls')),
        )


Django-simple-captcha 0.4.3 and later supports both Django 1.7's new migrations and South migrations: if you are using South and Django < 1.7, you must define the following in your settings::

        SOUTH_MIGRATION_MODULES = {
            'captcha': 'captcha.south_migrations',
        }


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

Passing arguments to the field
------------------------------

``CaptchaField`` takes a few optional arguements:

* ``output_format`` will let you format the layout of the rendered field. Defaults to the value defined in : :ref:`output_format_ref`.
* ``id_prefix`` Optional prefix that will be added to the ID attribute in the generated fields and labels, to be used when e.g. several Captcha fields are being displayed on a same page. (added in version 0.4.4)

Example usage for ajax form
---------------------------

An example CAPTCHA validation in AJAX::

    from django.views.generic.edit import CreateView
    from captcha.storages import storage
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

                to_json_response['new_cptch_key'] = storage.generate_key()
                to_json_response['new_cptch_image'] = captcha_image_url(to_json_response['new_cptch_key'])

                return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        def form_valid(self, form):
            form.save()
            if self.request.is_ajax():
                to_json_response = dict()
                to_json_response['status'] = 1

                to_json_response['new_cptch_key'] = storage.generate_key()
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
