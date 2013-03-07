from captcha.conf import settings
from captcha.models import CaptchaStore, get_safe_now
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse,  NoReverseMatch
from django.forms import ValidationError
from django.forms.fields import CharField, MultiValueField
from django.forms.widgets import TextInput, MultiWidget, HiddenInput
from django.utils.translation import ugettext_lazy as _


class CaptchaTextInput(MultiWidget):
    def __init__(self, attrs=None, **kwargs):
        self._args = kwargs
        widgets = (
            HiddenInput(attrs),
            TextInput(attrs),
        )
        self._args['output_format'] = self._args.get('output_format') or settings.CAPTCHA_OUTPUT_FORMAT

        for key in ('image', 'hidden_field', 'text_field'):
            if '%%(%s)s' % key not in self._args['output_format']:
                raise ImproperlyConfigured('All of %s must be present in your CAPTCHA_OUTPUT_FORMAT setting. Could not find %s' % (
                    ', '.join(['%%(%s)s' % k for k in ('image', 'hidden_field', 'text_field')]),
                    '%%(%s)s' % key
                ))
        super(CaptchaTextInput, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(',')
        return [None, None]

    def format_output(self, rendered_widgets):
        hidden_field, text_field = rendered_widgets
        return self._args['output_format'] % dict(image=self.image_and_audio, hidden_field=hidden_field, text_field=text_field)

    def render(self, name, value, attrs=None):
        try:
            reverse('captcha-image', args=('dummy',))
        except NoReverseMatch:
            raise ImproperlyConfigured('Make sure you\'ve included captcha.urls as explained in the INSTALLATION section on http://readthedocs.org/docs/django-simple-captcha/en/latest/usage.html#installation')

        # store = CaptchaStore()
        key = CaptchaStore.generate_key()
        value = [key, u'']

        self.image_and_audio = '<img src="%s" alt="captcha" class="captcha" />' % reverse('captcha-image', kwargs=dict(key=key))
        if settings.CAPTCHA_FLITE_PATH:
            self.image_and_audio = '<a href="%s" title="%s">%s</a>' % (reverse('captcha-audio', kwargs=dict(key=key)), str(_('Play CAPTCHA as audio file')), self.image_and_audio)
        return super(CaptchaTextInput, self).render(name, value, attrs=attrs)

    # This probably needs some more love
    def id_for_label(self, id_):
        if id_:
            id_ += '_1'
        return id_


class CaptchaField(MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (
            CharField(show_hidden_initial=True),
            CharField(),
        )
        if 'error_messages' not in kwargs or 'invalid' not in kwargs.get('error_messages'):
            if 'error_messages' not in kwargs:
                kwargs['error_messages'] = dict()
            kwargs['error_messages'].update(dict(invalid=_('Invalid CAPTCHA')))

        widget = kwargs.pop('widget', None) or CaptchaTextInput(output_format=kwargs.pop('output_format', None))

        super(CaptchaField, self).__init__(fields=fields, widget=widget, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)
        return None

    def clean(self, value):
        super(CaptchaField, self).clean(value)
        response, value[1] = value[1].strip().lower(), ''
        CaptchaStore.remove_expired()
        if settings.CATPCHA_TEST_MODE and response.lower() == 'passed':
            # automatically pass the test
            try:
                # try to delete the captcha based on its hash
                CaptchaStore.objects.get(hashkey=value[0]).delete()
            except Exception:
                # ignore errors
                pass
        else:
            try:
                CaptchaStore.objects.get(response=response, hashkey=value[0], expiration__gt=get_safe_now()).delete()
            except Exception:
                raise ValidationError(getattr(self, 'error_messages', dict()).get('invalid', _('Invalid CAPTCHA')))
        return value
