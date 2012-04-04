from django.forms.fields import CharField, MultiValueField
from django.forms import ValidationError
from django.forms.widgets import TextInput, MultiWidget, HiddenInput
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse,  NoReverseMatch
from captcha.models import CaptchaStore
from captcha.conf import settings
import datetime

class CaptchaTextInput(MultiWidget):
    def __init__(self,attrs=None, **kwargs):
        self._args = kwargs
        widgets = (
            HiddenInput(attrs),
            TextInput(attrs),
        )
        
        for key in ('image','hidden_field','text_field'):
            if '%%(%s)s'%key not in self._args.get('output_format'):
                raise ImproperlyConfigured('All of %s must be present in your CAPTCHA_OUTPUT_FORMAT setting. Could not find %s' %(
                    ', '.join(['%%(%s)s'%k for k in ('image','hidden_field','text_field')]),
                    '%%(%s)s'%key
                ))
        
        
        super(CaptchaTextInput,self).__init__(widgets,attrs)
    
    def decompress(self,value):
        if value:
            return value.split(',')
        return [None,None]
    
    def format_output(self, rendered_widgets):
        hidden_field, text_field = rendered_widgets
        return self._args.get('output_format') %dict(image=self.image_and_audio, hidden_field=hidden_field, text_field=text_field)
        
    def render(self, name, value, attrs=None):
        
        try:
            image_url = reverse('captcha-image', args=('dummy',))
        except NoReverseMatch,e:
            raise ImproperlyConfigured('Make sure you\'ve included captcha.urls as explained in the INSTALLATION section on http://code.google.com/p/django-simple-captcha/')
        
        
        challenge, response = settings.get_challenge()()
        
        store = CaptchaStore.objects.create(challenge=challenge,response=response)
        key = store.hashkey
        value = [key, u'']
        
        self.image_and_audio = '<img src="%s" alt="captcha" class="captcha" />' %reverse('captcha-image',kwargs=dict(key=key))
        if settings.CAPTCHA_FLITE_PATH:
            self.image_and_audio = '<a href="%s" title="%s">%s</a>' %( reverse('captcha-audio', kwargs=dict(key=key)), unicode(_('Play captcha as audio file')), self.image_and_audio)
        
        return super(CaptchaTextInput, self).render(name, value, attrs=attrs)

    # This probably needs some more love
    def id_for_label(self, id_):
        return 'id_captcha_1'

class CaptchaField(MultiValueField):
    
    def __init__(self, *args,**kwargs):
        fields = (
            CharField(show_hidden_initial=True), 
            CharField(),
        )
        if 'error_messages' not in kwargs or 'invalid' not in kwargs.get('error_messages'):
            if 'error_messages' not in kwargs:
                kwargs['error_messages'] = dict()
            kwargs['error_messages'].update(dict(invalid=_('Invalid CAPTCHA')))

        widget_kwargs = dict(
            output_format = kwargs.get('output_format',None) or settings.CAPTCHA_OUTPUT_FORMAT
        )
        for k in ('output_format',):
            if k in kwargs:
                del(kwargs[k])
        
        super(CaptchaField,self).__init__(fields=fields, widget=CaptchaTextInput(**widget_kwargs), *args, **kwargs)

    
    def compress(self,data_list):
        if data_list:
            return ','.join(data_list)
        return None
        
    def clean(self, value):
        super(CaptchaField, self).clean(value)
        response, value[1] = value[1].strip().lower(), ''
        CaptchaStore.remove_expired()
        try:
            store = CaptchaStore.objects.get(response=response, hashkey=value[0], expiration__gt=datetime.datetime.now())
            store.delete()
        except Exception:
            raise ValidationError(getattr(self,'error_messages',dict()).get('invalid', _('Invalid CAPTCHA')))
        return value
