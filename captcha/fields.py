from captcha.conf import settings
from captcha.models import CaptchaStore
import django
from django.core.exceptions import ImproperlyConfigured
if django.VERSION < (1, 10):  # NOQA
    from django.core.urlresolvers import reverse, NoReverseMatch  # NOQA
else:  # NOQA
    from django.urls import reverse, NoReverseMatch  # NOQA
from django.forms import ValidationError
from django.forms.fields import CharField, MultiValueField
from django.forms.widgets import TextInput, MultiWidget, HiddenInput
from django.utils.translation import ugettext_lazy
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from six import u


class BaseCaptchaTextInput(MultiWidget):
    """
    Base class for Captcha widgets
    """
    def __init__(self, attrs=None):
        widgets = (
            HiddenInput(attrs),
            TextInput(attrs),
        )
        super(BaseCaptchaTextInput, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(',')
        return [None, None]

    def fetch_captcha_store(self, name, value, attrs=None, generator=None):
        """
        Fetches a new CaptchaStore
        This has to be called inside render
        """
        try:
            reverse('captcha-image', args=('dummy',))
        except NoReverseMatch:
            raise ImproperlyConfigured('Make sure you\'ve included captcha.urls as explained in the INSTALLATION section on http://readthedocs.org/docs/django-simple-captcha/en/latest/usage.html#installation')

        if settings.CAPTCHA_GET_FROM_POOL:
            key = CaptchaStore.pick()
        else:
            key = CaptchaStore.generate_key(generator)

        # these can be used by format_output and render
        self._value = [key, u('')]
        self._key = key
        self.id_ = self.build_attrs(attrs).get('id', None)

    def id_for_label(self, id_):
        if id_:
            return id_ + '_1'
        return id_

    def image_url(self):
        return reverse('captcha-image', kwargs={'key': self._key})

    def audio_url(self):
        return reverse('captcha-audio', kwargs={'key': self._key}) if settings.CAPTCHA_FLITE_PATH else None

    def refresh_url(self):
        return reverse('captcha-refresh')


class CaptchaTextInput(BaseCaptchaTextInput):
    def __init__(self, attrs=None, **kwargs):
        self._args = kwargs
        self._args['output_format'] = self._args.get('output_format') or settings.CAPTCHA_OUTPUT_FORMAT
        self._args['field_template'] = self._args.get('field_template') or settings.CAPTCHA_FIELD_TEMPLATE
        # self._args['id_prefix'] = self._args.get('id_prefix')

        if self._args['output_format'] is None and self._args['field_template'] is None:
            raise ImproperlyConfigured('You MUST define either CAPTCHA_FIELD_TEMPLATE or CAPTCHA_OUTPUT_FORMAT setting. Please refer to http://readthedocs.org/docs/django-simple-captcha/en/latest/usage.html#installation')

        if self._args['output_format']:
            for key in ('image', 'hidden_field', 'text_field'):
                if '%%(%s)s' % key not in self._args['output_format']:
                    raise ImproperlyConfigured('All of %s must be present in your CAPTCHA_OUTPUT_FORMAT setting. Could not find %s' % (
                        ', '.join(['%%(%s)s' % k for k in ('image', 'hidden_field', 'text_field')]),
                        '%%(%s)s' % key
                    ))

        super(CaptchaTextInput, self).__init__(attrs)

    def build_attrs(self, *args, **kwargs):
        ret = super(CaptchaTextInput, self).build_attrs(*args, **kwargs)
        if self._args.get('id_prefix') and 'id' in ret:
            ret['id'] = '%s_%s' % (self._args.get('id_prefix'), ret['id'])
        return ret

    def id_for_label(self, id_):
        ret = super(CaptchaTextInput, self).id_for_label(id_)
        if self._args.get('id_prefix') and 'id' in ret:
            ret = '%s_%s' % (self._args.get('id_prefix'), ret)
        return ret

    def format_output(self, rendered_widgets):
        # hidden_field, text_field = rendered_widgets
        if self._args['output_format']:
            ret = self._args['output_format'] % {
                'image': self.image_and_audio,
                'hidden_field': self.hidden_field,
                'text_field': self.text_field
            }
            return ret

        elif self._args['field_template']:
            context = {
                'image': mark_safe(self.image_and_audio),
                'hidden_field': mark_safe(self.hidden_field),
                'text_field': mark_safe(self.text_field)
            }
            return render_to_string(settings.CAPTCHA_FIELD_TEMPLATE, context)

    def render(self, name, value, attrs=None, renderer=None):
        self.fetch_captcha_store(name, value, attrs, self._args.get('generator'))

        context = {
            'image': self.image_url(),
            'name': name,
            'key': self._key,
            'id': u'%s_%s' % (self._args.get('id_prefix'), attrs.get('id')) if self._args.get('id_prefix') else attrs.get('id')
        }
        if settings.CAPTCHA_FLITE_PATH:
            context.update({'audio': self.audio_url()})

        self.image_and_audio = render_to_string(settings.CAPTCHA_IMAGE_TEMPLATE, context)
        self.hidden_field = render_to_string(settings.CAPTCHA_HIDDEN_FIELD_TEMPLATE, context)
        self.text_field = render_to_string(settings.CAPTCHA_TEXT_FIELD_TEMPLATE, context)

        extra_kwargs = {}
        if django.VERSION >= (1, 11):
            # https://docs.djangoproject.com/en/1.11/ref/forms/widgets/#django.forms.Widget.render
            extra_kwargs['renderer'] = renderer

        return super(CaptchaTextInput, self).render(name, self._value, attrs=attrs, **extra_kwargs)

    def _render(self, template_name, context, renderer=None):
        return self.format_output(None)


class CaptchaField(MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (
            CharField(show_hidden_initial=True),
            CharField(),
        )
        if 'error_messages' not in kwargs or 'invalid' not in kwargs.get('error_messages'):
            if 'error_messages' not in kwargs:
                kwargs['error_messages'] = {}
            kwargs['error_messages'].update({'invalid': ugettext_lazy('Invalid CAPTCHA')})

        kwargs['widget'] = kwargs.pop('widget', CaptchaTextInput(
            output_format=kwargs.pop('output_format', None),
            id_prefix=kwargs.pop('id_prefix', None),
            generator=kwargs.pop('generator', None)
        ))

        super(CaptchaField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)
        return None

    def clean(self, value):
        super(CaptchaField, self).clean(value)
        response, value[1] = (value[1] or '').strip().lower(), ''
        if not settings.CAPTCHA_GET_FROM_POOL:
            CaptchaStore.remove_expired()
        if settings.CAPTCHA_TEST_MODE and response.lower() == 'passed':
            # automatically pass the test
            try:
                # try to delete the captcha based on its hash
                CaptchaStore.objects.get(hashkey=value[0]).delete()
            except CaptchaStore.DoesNotExist:
                # ignore errors
                pass
        elif not self.required and not response:
            pass
        else:
            try:
                CaptchaStore.objects.get(response=response, hashkey=value[0], expiration__gt=timezone.now()).delete()
            except CaptchaStore.DoesNotExist:
                raise ValidationError(getattr(self, 'error_messages', {}).get('invalid', ugettext_lazy('Invalid CAPTCHA')))
        return value
