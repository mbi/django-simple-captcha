from captcha.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, NoReverseMatch
from django.forms import ValidationError
from django.forms.fields import CharField, MultiValueField
from django.forms.widgets import TextInput, MultiWidget, HiddenInput
from django.utils.translation import ugettext, ugettext_lazy
from six import u
from .backends.base import BaseStore


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

    def fetch_captcha_store(self, name, value, attrs=None):
        """
        Fetches a new CaptchaStore
        This has to be called inside render
        """

        CaptchaStore = None
        if settings.CAPTCHA_STORE == 'SESSION':
            from .backends.session import SessionStore
            CaptchaStore = SessionStore()
        elif settings.CAPTCHA_STORE == 'DB':
            from .backends.db import DBStore
            CaptchaStore = DBStore()
        else:
            raise ImproperlyConfigured

        try:
            reverse('captcha-image', args=('dummy',))
        except NoReverseMatch:
            raise ImproperlyConfigured('Make sure you\'ve included captcha.urls as explained in the INSTALLATION section on http://readthedocs.org/docs/django-simple-captcha/en/latest/usage.html#installation')

        key = CaptchaStore.generate_key()

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
        self._args['id_prefix'] = self._args.get('id_prefix')

        for key in ('image', 'hidden_field', 'text_field'):
            if '%%(%s)s' % key not in self._args['output_format']:
                raise ImproperlyConfigured('All of %s must be present in your CAPTCHA_OUTPUT_FORMAT setting. Could not find %s' % (
                    ', '.join(['%%(%s)s' % k for k in ('image', 'hidden_field', 'text_field')]),
                    '%%(%s)s' % key
                ))
        super(CaptchaTextInput, self).__init__(attrs)

    def build_attrs(self, extra_attrs=None, **kwargs):
        ret = super(CaptchaTextInput, self).build_attrs(extra_attrs, **kwargs)
        if self._args.get('id_prefix') and 'id' in ret:
            ret['id'] = '%s_%s' % (self._args.get('id_prefix'), ret['id'])
        return ret

    def id_for_label(self, id_):
        ret = super(CaptchaTextInput, self).id_for_label(id_)
        if self._args.get('id_prefix') and 'id' in ret:
            ret = '%s_%s' % (self._args.get('id_prefix'), ret)
        return ret

    def format_output(self, rendered_widgets):
        hidden_field, text_field = rendered_widgets
        text_field = text_field.replace('<input', '<input autocomplete="off"')
        return self._args['output_format'] % {
            'image': self.image_and_audio,
            'hidden_field': hidden_field,
            'text_field': text_field
        }

    def render(self, name, value, attrs=None):
        self.fetch_captcha_store(name, value, attrs)

        self.image_and_audio = '<img src="%s" alt="captcha" class="captcha" />' % self.image_url()
        if settings.CAPTCHA_FLITE_PATH:
            self.image_and_audio = '<a href="%s" title="%s">%s</a>' % (self.audio_url(), ugettext('Play CAPTCHA as audio file'), self.image_and_audio)
        return super(CaptchaTextInput, self).render(name, self._value, attrs=attrs)


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
            id_prefix=kwargs.pop('id_prefix', None)
        ))

        super(CaptchaField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)
        return None

    def clean(self, value):
        CaptchaStore = None
        if settings.CAPTCHA_STORE == 'SESSION':
            from .backends.session import SessionStore
            CaptchaStore = SessionStore()
        elif settings.CAPTCHA_STORE == 'DB':
            from .backends.db import DBStore
            CaptchaStore = DBStore()
        else:
            raise ImproperlyConfigured

        super(CaptchaField, self).clean(value)
        response, value[1] = (value[1] or '').strip().lower(), ''
        CaptchaStore.remove_expired()
        if settings.CAPTCHA_TEST_MODE and response.lower() == 'passed':
            # automatically pass the test
            try:
                # try to delete the captcha based on its hash
                CaptchaStore.get(hashkey=value[0]).delete()
            except BaseStore.DoesNotExist:
                # ignore errors
                pass
        elif not self.required and not response:
            pass
        else:
            try:
                CaptchaStore.get(response=response, hashkey=value[0], allow_expired=False).delete()
            except BaseStore.DoesNotExist:
                raise ValidationError(getattr(self, 'error_messages', {}).get('invalid', ugettext_lazy('Invalid CAPTCHA')))
        return value
