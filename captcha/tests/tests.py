# -*- coding: utf-8 -*-
from captcha.conf import settings
from captcha import storages
from captcha import views
from captcha import fields
from captcha.management.commands import captcha_clean
from captcha.fields import CaptchaField, CaptchaTextInput
from captcha.helpers import get_safe_now
from captcha.storages import get_storage
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.utils.translation import ugettext_lazy
import datetime
import json
import re
import six
import os
try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from six import u, text_type

try:
    from PIL import Image
except ImportError:
    import Image  # NOQA

# store original storage setting
orig_storage = storages.storage


class OverrideStorageMixin(object):
    """
    Use for test cases with different storage setting
    """

    new_storage = get_storage({
        'BACKEND': 'captcha.storages.cache.CacheStorage',
    })

    def setUp(self):

        storages.storage = self.new_storage
        views.storage = storages.storage
        fields.storage = storages.storage
        captcha_clean.storage = storages.storage

        super(OverrideStorageMixin, self).setUp()

    def tearDown(self):

        super(OverrideStorageMixin, self).tearDown()

        storages.storage = orig_storage
        views.storage = orig_storage
        fields.storage = orig_storage
        captcha_clean.storage = orig_storage


@override_settings(ROOT_URLCONF='captcha.tests.urls')
class CaptchaCase(TestCase):

    def setUp(self):

        self.stores = {}
        self.__current_settings_output_format = settings.CAPTCHA_OUTPUT_FORMAT
        self.__current_settings_dictionary = settings.CAPTCHA_WORDS_DICTIONARY
        self.__current_settings_punctuation = settings.CAPTCHA_PUNCTUATION

        tested_helpers = ['captcha.helpers.math_challenge', 'captcha.helpers.random_char_challenge', 'captcha.helpers.unicode_challenge']
        if os.path.exists('/usr/share/dict/words'):
            settings.CAPTCHA_WORDS_DICTIONARY = '/usr/share/dict/words'
            settings.CAPTCHA_PUNCTUATION = ';-,.'
            tested_helpers.append('captcha.helpers.word_challenge')
            tested_helpers.append('captcha.helpers.huge_words_and_punctuation_challenge')
        for helper in tested_helpers:
            challenge, response = settings._callable_from_string(helper)()
            self.stores[helper.rsplit('.', 1)[-1].replace('_challenge', '_store')] = storages.storage.create(challenge=challenge, response=response)
        challenge, response = settings.get_challenge()()
        self.stores['default_store'] = storages.storage.create(challenge=challenge, response=response)
        self.default_store = self.stores['default_store']

    def tearDown(self):
        settings.CAPTCHA_OUTPUT_FORMAT = self.__current_settings_output_format
        settings.CAPTCHA_WORDS_DICTIONARY = self.__current_settings_dictionary
        settings.CAPTCHA_PUNCTUATION = self.__current_settings_punctuation

    def __extract_hash_and_response(self, r):
        hash_ = re.findall(r'value="([0-9a-f]+)"', str(r.content))[0]
        response = storages.storage.get(hashkey=hash_).response
        return hash_, response

    def test_image(self):
        for key in [store.hashkey for store in six.itervalues(self.stores)]:
            response = self.client.get(reverse('captcha-image', kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.has_header('content-type'))
            self.assertEqual(response._headers.get('content-type'), ('Content-Type', 'image/png'))

    def test_audio(self):
        if not settings.CAPTCHA_FLITE_PATH:
            return
        for key in (self.stores.get('math_store').hashkey, self.stores.get('math_store').hashkey, self.default_store.hashkey):
            response = self.client.get(reverse('captcha-audio', kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(response.content) > 1024)
            self.assertTrue(response.has_header('content-type'))
            self.assertEqual(response._headers.get('content-type'), ('Content-Type', 'audio/x-wav'))

    def test_form_submit(self):
        r = self.client.get(reverse('captcha-test'))
        self.assertEqual(r.status_code, 200)
        hash_, response = self.__extract_hash_and_response(r)

        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_, captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(str(r.content).find('Form validated') > 0)

        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_, captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(str(r.content).find('Form validated') > 0)

    def test_modelform(self):
        r = self.client.get(reverse('captcha-test-model-form'))
        self.assertEqual(r.status_code, 200)
        hash_, response = self.__extract_hash_and_response(r)

        r = self.client.post(reverse('captcha-test-model-form'), dict(captcha_0=hash_, captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(str(r.content).find('Form validated') > 0)

        r = self.client.post(reverse('captcha-test-model-form'), dict(captcha_0=hash_, captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(str(r.content).find('Form validated') > 0)

    def test_wrong_submit(self):
        for urlname in ('captcha-test', 'captcha-test-model-form'):
            r = self.client.get(reverse(urlname))
            self.assertEqual(r.status_code, 200)
            r = self.client.post(reverse(urlname), dict(captcha_0='abc', captcha_1='wrong response', subject='xxx', sender='asasd@asdasd.com'))
            self.assertFormError(r, 'form', 'captcha', ugettext_lazy('Invalid CAPTCHA'))

    def test_deleted_expired(self):
        challenge, response = settings.get_challenge()()
        expiration = get_safe_now() - datetime.timedelta(minutes=5)
        expired_store = storages.storage.create(challenge=challenge, response=response, expiration=expiration)
        hash_ = expired_store.hashkey
        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_, captcha_1=self.default_store.response, subject='xxx', sender='asasd@asdasd.com'))

        self.assertEqual(r.status_code, 200)
        self.assertFalse('Form validated' in str(r.content))

        # expired -> deleted
        try:
            storages.storage.get(hashkey=hash_)
            self.fail()
        except:
            pass

    def test_custom_error_message(self):
        r = self.client.get(reverse('captcha-test-custom-error-message'))
        self.assertEqual(r.status_code, 200)
        # Wrong answer
        r = self.client.post(reverse('captcha-test-custom-error-message'), dict(captcha_0='abc', captcha_1='wrong response'))
        self.assertFormError(r, 'form', 'captcha', 'TEST CUSTOM ERROR MESSAGE')
        # empty answer
        r = self.client.post(reverse('captcha-test-custom-error-message'), dict(captcha_0='abc', captcha_1=''))
        self.assertFormError(r, 'form', 'captcha', ugettext_lazy('This field is required.'))

    def test_repeated_challenge(self):
        storages.storage.create(challenge='xxx', response='xxx')
        try:
            storages.storage.create(challenge='xxx', response='xxx')
        except Exception:
            self.fail()

    def test_repeated_challenge_form_submit(self):
        __current_challange_function = settings.CAPTCHA_CHALLENGE_FUNCT
        for urlname in ('captcha-test', 'captcha-test-model-form'):
            settings.CAPTCHA_CHALLENGE_FUNCT = 'captcha.tests.trivial_challenge'

            r1 = self.client.get(reverse(urlname))
            r2 = self.client.get(reverse(urlname))
            self.assertEqual(r1.status_code, 200)
            self.assertEqual(r2.status_code, 200)
            if re.findall(r'value="([0-9a-f]+)"', str(r1.content)):
                hash_1 = re.findall(r'value="([0-9a-f]+)"', str(r1.content))[0]
            else:
                self.fail()

            if re.findall(r'value="([0-9a-f]+)"', str(r2.content)):
                hash_2 = re.findall(r'value="([0-9a-f]+)"', str(r2.content))[0]
            else:
                self.fail()
            try:
                store_1 = storages.storage.get(hashkey=hash_1)
                store_2 = storages.storage.get(hashkey=hash_2)
            except:
                self.fail()

            self.assertTrue(store_1.hashkey != store_2.hashkey)
            self.assertTrue(store_1.response == store_2.response)
            self.assertTrue(hash_1 != hash_2)

            r1 = self.client.post(reverse(urlname), dict(captcha_0=hash_1, captcha_1=store_1.response, subject='xxx', sender='asasd@asdasd.com'))
            self.assertEqual(r1.status_code, 200)
            self.assertTrue(str(r1.content).find('Form validated') > 0)

            try:
                store_2 = storages.storage.get(hashkey=hash_2)
            except:
                self.fail()

            r2 = self.client.post(reverse(urlname), dict(captcha_0=hash_2, captcha_1=store_2.response, subject='xxx', sender='asasd@asdasd.com'))
            self.assertEqual(r2.status_code, 200)
            self.assertTrue(str(r2.content).find('Form validated') > 0)
        settings.CAPTCHA_CHALLENGE_FUNCT = __current_challange_function

    def test_output_format(self):
        for urlname in ('captcha-test', 'captcha-test-model-form'):
            settings.CAPTCHA_OUTPUT_FORMAT = u('%(image)s<p>Hello, captcha world</p>%(hidden_field)s%(text_field)s')
            r = self.client.get(reverse(urlname))
            self.assertEqual(r.status_code, 200)
            self.assertTrue('<p>Hello, captcha world</p>' in str(r.content))

    def test_invalid_output_format(self):
        for urlname in ('captcha-test', 'captcha-test-model-form'):
            settings.CAPTCHA_OUTPUT_FORMAT = u('%(image)s')
            try:
                self.client.get(reverse(urlname))
                self.fail()
            except ImproperlyConfigured as e:
                self.assertTrue('CAPTCHA_OUTPUT_FORMAT' in str(e))

    def test_per_form_format(self):
        settings.CAPTCHA_OUTPUT_FORMAT = u('%(image)s testCustomFormatString %(hidden_field)s %(text_field)s')
        r = self.client.get(reverse('captcha-test'))
        self.assertTrue('testCustomFormatString' in str(r.content))
        r = self.client.get(reverse('test_per_form_format'))
        self.assertTrue('testPerFieldCustomFormatString' in str(r.content))

    def test_issue31_proper_abel(self):
        settings.CAPTCHA_OUTPUT_FORMAT = u('%(image)s %(hidden_field)s %(text_field)s')
        r = self.client.get(reverse('captcha-test'))
        self.assertTrue('<label for="id_captcha_1"' in str(r.content))

    def test_refresh_view(self):
        r = self.client.get(reverse('captcha-refresh'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        try:
            new_data = json.loads(six.text_type(r.content, encoding='ascii'))
            self.assertTrue('image_url' in new_data)
        except:
            self.fail()

    def test_content_length(self):
        for key in [store.hashkey for store in six.itervalues(self.stores)]:
            response = self.client.get(reverse('captcha-image', kwargs=dict(key=key)))
            self.assertTrue(response.has_header('content-length'))
            self.assertTrue(response['content-length'].isdigit())
            self.assertTrue(int(response['content-length']))

    def test_issue12_proper_instantiation(self):
        """
        This test covers a default django field and widget behavior
        It not assert anything. If something is wrong it will raise a error!
        """
        settings.CAPTCHA_OUTPUT_FORMAT = u('%(image)s %(hidden_field)s %(text_field)s')
        widget = CaptchaTextInput(attrs={'class': 'required'})
        CaptchaField(widget=widget)

    def test_test_mode_issue15(self):
        __current_test_mode_setting = settings.CAPTCHA_TEST_MODE
        settings.CAPTCHA_TEST_MODE = False
        r = self.client.get(reverse('captcha-test'))
        self.assertEqual(r.status_code, 200)
        r = self.client.post(reverse('captcha-test'), dict(captcha_0='abc', captcha_1='wrong response', subject='xxx', sender='asasd@asdasd.com'))
        self.assertFormError(r, 'form', 'captcha', ugettext_lazy('Invalid CAPTCHA'))

        settings.CAPTCHA_TEST_MODE = True
        # Test mode, only 'PASSED' is accepted
        r = self.client.get(reverse('captcha-test'))
        self.assertEqual(r.status_code, 200)
        r = self.client.post(reverse('captcha-test'), dict(captcha_0='abc', captcha_1='wrong response', subject='xxx', sender='asasd@asdasd.com'))
        self.assertFormError(r, 'form', 'captcha', ugettext_lazy('Invalid CAPTCHA'))

        r = self.client.get(reverse('captcha-test'))
        self.assertEqual(r.status_code, 200)
        r = self.client.post(reverse('captcha-test'), dict(captcha_0='abc', captcha_1='passed', subject='xxx', sender='asasd@asdasd.com'))
        self.assertTrue(str(r.content).find('Form validated') > 0)
        settings.CAPTCHA_TEST_MODE = __current_test_mode_setting

    def test_get_version(self):
        import captcha
        captcha.get_version(True)

    def test_missing_value(self):
        r = self.client.get(reverse('captcha-test-non-required'))
        self.assertEqual(r.status_code, 200)
        hash_, response = self.__extract_hash_and_response(r)

        # Empty response is okay when required is False
        r = self.client.post(reverse('captcha-test-non-required'), dict(subject='xxx', sender='asasd@asdasd.com'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(str(r.content).find('Form validated') > 0)

        # But a valid response is okay, too
        r = self.client.get(reverse('captcha-test-non-required'))
        self.assertEqual(r.status_code, 200)
        hash_, response = self.__extract_hash_and_response(r)

        r = self.client.post(reverse('captcha-test-non-required'), dict(captcha_0=hash_, captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(str(r.content).find('Form validated') > 0)

    def test_autocomplete_off(self):
        r = self.client.get(reverse('captcha-test'))
        self.assertTrue('<input autocomplete="off" ' in six.text_type(r.content))

    def test_autocomplete_not_on_hidden_input(self):
        r = self.client.get(reverse('captcha-test'))
        self.assertFalse('autocomplete="off" type="hidden" name="captcha_0"' in six.text_type(r.content))
        self.assertFalse('autocomplete="off" id="id_captcha_0" name="captcha_0" type="hidden"' in six.text_type(r.content))

    def test_transparent_background(self):
        __current_test_mode_setting = settings.CAPTCHA_BACKGROUND_COLOR
        settings.CAPTCHA_BACKGROUND_COLOR = "transparent"
        for key in [store.hashkey for store in six.itervalues(self.stores)]:
            response = self.client.get(reverse('captcha-image', kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.has_header('content-type'))
            self.assertEqual(response._headers.get('content-type'), ('Content-Type', 'image/png'))

        settings.CAPTCHA_BACKGROUND_COLOR = __current_test_mode_setting

    def test_expired_captcha_returns_410(self):
        for key in [store.hashkey for store in six.itervalues(self.stores)]:
            response = self.client.get(reverse('captcha-image', kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            storages.storage.delete(hashkey=key)
            response = self.client.get(reverse('captcha-image', kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 410)

    def test_id_prefix(self):
        r = self.client.get(reverse('captcha-test-id-prefix'))
        self.assertTrue('<label for="form1_id_captcha1_1">Captcha1:</label>' in six.text_type(r.content))
        self.assertTrue('id="form1_id_captcha1_1"' in six.text_type(r.content))
        self.assertTrue('<label for="form2_id_captcha2_1">Captcha2:</label>' in six.text_type(r.content))
        self.assertTrue('id="form2_id_captcha2_1"' in six.text_type(r.content))

    def test_image_size(self):
        __current_test_mode_setting = settings.CAPTCHA_IMAGE_SIZE
        for key in [store.hashkey for store in six.itervalues(self.stores)]:
            settings.CAPTCHA_IMAGE_SIZE = (201, 97)
            response = self.client.get(reverse('captcha-image', kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.has_header('content-type'))
            self.assertEqual(response._headers.get('content-type'), ('Content-Type', 'image/png'))
            self.assertEqual(Image.open(StringIO(response.content)).size, (201, 97))

        settings.CAPTCHA_IMAGE_SIZE = __current_test_mode_setting

    def test_multiple_fonts(self):
        vera = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'Vera.ttf')
        __current_test_mode_setting = settings.CAPTCHA_FONT_PATH
        settings.CAPTCHA_FONT_PATH = vera

        for key in [store.hashkey for store in six.itervalues(self.stores)]:
            response = self.client.get(reverse('captcha-image', kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response._headers.get('content-type'), ('Content-Type', 'image/png'))

        settings.CAPTCHA_FONT_PATH = [vera, vera, vera]
        for key in [store.hashkey for store in six.itervalues(self.stores)]:
            response = self.client.get(reverse('captcha-image', kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response._headers.get('content-type'), ('Content-Type', 'image/png'))

        settings.CAPTCHA_FONT_PATH = False
        for key in [store.hashkey for store in six.itervalues(self.stores)]:
            try:
                response = self.client.get(reverse('captcha-image', kwargs=dict(key=key)))
                self.fail()
            except ImproperlyConfigured:
                pass

        settings.CAPTCHA_FONT_PATH = __current_test_mode_setting

    def test_template_overrides(self):
        __current_test_mode_setting = settings.CAPTCHA_IMAGE_TEMPLATE
        settings.CAPTCHA_IMAGE_TEMPLATE = 'captcha_test/image.html'

        for urlname in ('captcha-test', 'captcha-test-model-form'):
            settings.CAPTCHA_CHALLENGE_FUNCT = 'captcha.tests.trivial_challenge'
            r = self.client.get(reverse(urlname))
            self.assertTrue('captcha-template-test' in six.text_type(r.content))
        settings.CAPTCHA_IMAGE_TEMPLATE = __current_test_mode_setting

    def test_math_challenge(self):
        __current_test_mode_setting = settings.CAPTCHA_MATH_CHALLENGE_OPERATOR
        settings.CAPTCHA_MATH_CHALLENGE_OPERATOR = '~'
        helper = 'captcha.helpers.math_challenge'
        challenge, response = settings._callable_from_string(helper)()

        while settings.CAPTCHA_MATH_CHALLENGE_OPERATOR not in challenge:
            challenge, response = settings._callable_from_string(helper)()

        self.assertEqual(response, text_type(eval(challenge.replace(settings.CAPTCHA_MATH_CHALLENGE_OPERATOR, '*')[:-1])))
        settings.CAPTCHA_MATH_CHALLENGE_OPERATOR = __current_test_mode_setting


class CaptchaCaseCacheStorage(OverrideStorageMixin, CaptchaCase):

    def test_default_store_from_cache(self):
        self.assertEqual(self.default_store.pk, None)


def trivial_challenge():
    return 'trivial', 'trivial'
