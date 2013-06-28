# -*- coding: utf-8 -*-
from captcha.conf import settings
from captcha.fields import CaptchaField, CaptchaTextInput
from captcha.models import CaptchaStore, get_safe_now
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext_lazy
import datetime
import json
import re
import six
import os


class CaptchaCase(TestCase):
    urls = 'captcha.tests.urls'

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
            self.stores[helper.rsplit('.', 1)[-1].replace('_challenge', '_store')], _ = CaptchaStore.objects.get_or_create(challenge=challenge, response=response)
        challenge, response = settings.get_challenge()()
        self.stores['default_store'], _ = CaptchaStore.objects.get_or_create(challenge=challenge, response=response)
        self.default_store = self.stores['default_store']

    def tearDown(self):
        settings.CAPTCHA_OUTPUT_FORMAT = self.__current_settings_output_format
        settings.CAPTCHA_WORDS_DICTIONARY = self.__current_settings_dictionary
        settings.CAPTCHA_PUNCTUATION = self.__current_settings_punctuation


    def __extract_hash_and_response(self, r):
        hash_ = re.findall(r'value="([0-9a-f]+)"', str(r.content))[0]
        response = CaptchaStore.objects.get(hashkey=hash_).response
        return hash_, response

    def testImages(self):
        for key in [store.hashkey for store in six.itervalues(self.stores)]:
            response = self.client.get(reverse('captcha-image', kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.has_header('content-type'))
            self.assertEqual(response._headers.get('content-type'), ('Content-Type', 'image/png'))

    def testAudio(self):
        if not settings.CAPTCHA_FLITE_PATH:
            return
        for key in (self.stores.get('math_store').hashkey, self.stores.get('math_store').hashkey, self.default_store.hashkey):
            response = self.client.get(reverse('captcha-audio', kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(response.content) > 1024)
            self.assertTrue(response.has_header('content-type'))
            self.assertEqual(response._headers.get('content-type'), ('Content-Type', 'audio/x-wav'))

    def testFormSubmit(self):
        r = self.client.get(reverse('captcha-test'))
        self.assertEqual(r.status_code, 200)
        hash_, response = self.__extract_hash_and_response(r)

        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_, captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(str(r.content).find('Form validated') > 0)

        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_, captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(str(r.content).find('Form validated') > 0)

    def testFormModelForm(self):
        r = self.client.get(reverse('captcha-test-model-form'))
        self.assertEqual(r.status_code, 200)
        hash_, response = self.__extract_hash_and_response(r)

        r = self.client.post(reverse('captcha-test-model-form'), dict(captcha_0=hash_, captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(str(r.content).find('Form validated') > 0)

        r = self.client.post(reverse('captcha-test-model-form'), dict(captcha_0=hash_, captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(str(r.content).find('Form validated') > 0)

    def testWrongSubmit(self):
        for urlname in ('captcha-test', 'captcha-test-model-form'):
            r = self.client.get(reverse(urlname))
            self.assertEqual(r.status_code, 200)
            r = self.client.post(reverse(urlname), dict(captcha_0='abc', captcha_1='wrong response', subject='xxx', sender='asasd@asdasd.com'))
            self.assertFormError(r, 'form', 'captcha', ugettext_lazy('Invalid CAPTCHA'))

    def testDeleteExpired(self):
        self.default_store.expiration = get_safe_now() - datetime.timedelta(minutes=5)
        self.default_store.save()
        hash_ = self.default_store.hashkey
        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_, captcha_1=self.default_store.response, subject='xxx', sender='asasd@asdasd.com'))

        self.assertEqual(r.status_code, 200)
        self.assertFalse('Form validated' in str(r.content))

        # expired -> deleted
        try:
            CaptchaStore.objects.get(hashkey=hash_)
            self.fail()
        except:
            pass

    def testCustomErrorMessage(self):
        r = self.client.get(reverse('captcha-test-custom-error-message'))
        self.assertEqual(r.status_code, 200)
        # Wrong answer
        r = self.client.post(reverse('captcha-test-custom-error-message'), dict(captcha_0='abc', captcha_1='wrong response'))
        self.assertFormError(r, 'form', 'captcha', 'TEST CUSTOM ERROR MESSAGE')
        # empty answer
        r = self.client.post(reverse('captcha-test-custom-error-message'), dict(captcha_0='abc', captcha_1=''))
        self.assertFormError(r, 'form', 'captcha', ugettext_lazy('This field is required.'))

    def testRepeatedChallenge(self):
        CaptchaStore.objects.create(challenge='xxx', response='xxx')
        try:
            CaptchaStore.objects.create(challenge='xxx', response='xxx')
        except Exception:
            self.fail()

    def testRepeatedChallengeFormSubmit(self):
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
                store_1 = CaptchaStore.objects.get(hashkey=hash_1)
                store_2 = CaptchaStore.objects.get(hashkey=hash_2)
            except:
                self.fail()

            self.assertTrue(store_1.pk != store_2.pk)
            self.assertTrue(store_1.response == store_2.response)
            self.assertTrue(hash_1 != hash_2)

            r1 = self.client.post(reverse(urlname), dict(captcha_0=hash_1, captcha_1=store_1.response, subject='xxx', sender='asasd@asdasd.com'))
            self.assertEqual(r1.status_code, 200)
            self.assertTrue(str(r1.content).find('Form validated') > 0)

            try:
                store_2 = CaptchaStore.objects.get(hashkey=hash_2)
            except:
                self.fail()

            r2 = self.client.post(reverse(urlname), dict(captcha_0=hash_2, captcha_1=store_2.response, subject='xxx', sender='asasd@asdasd.com'))
            self.assertEqual(r2.status_code, 200)
            self.assertTrue(str(r2.content).find('Form validated') > 0)
        settings.CAPTCHA_CHALLENGE_FUNCT = __current_challange_function

    def testOutputFormat(self):
        for urlname in ('captcha-test', 'captcha-test-model-form'):
            settings.CAPTCHA_OUTPUT_FORMAT = u'%(image)s<p>Hello, captcha world</p>%(hidden_field)s%(text_field)s'
            r = self.client.get(reverse(urlname))
            self.assertEqual(r.status_code, 200)
            self.assertTrue('<p>Hello, captcha world</p>' in str(r.content))

    def testInvalidOutputFormat(self):
        __current_settings_debug = django_settings.DEBUG
        for urlname in ('captcha-test', 'captcha-test-model-form'):
            # we turn on DEBUG because CAPTCHA_OUTPUT_FORMAT is only checked debug

            django_settings.DEBUG = True
            settings.CAPTCHA_OUTPUT_FORMAT = u'%(image)s'
            try:
                self.client.get(reverse(urlname))
                self.fail()
            except ImproperlyConfigured as e:
                self.assertTrue('CAPTCHA_OUTPUT_FORMAT' in str(e))
        django_settings.DEBUG = __current_settings_debug

    def testPerFormFormat(self):
        settings.CAPTCHA_OUTPUT_FORMAT = u'%(image)s testCustomFormatString %(hidden_field)s %(text_field)s'
        r = self.client.get(reverse('captcha-test'))
        self.assertTrue('testCustomFormatString' in str(r.content))
        r = self.client.get(reverse('test_per_form_format'))
        self.assertTrue('testPerFieldCustomFormatString' in str(r.content))

    def testIssue31ProperLabel(self):
        settings.CAPTCHA_OUTPUT_FORMAT = u'%(image)s %(hidden_field)s %(text_field)s'
        r = self.client.get(reverse('captcha-test'))
        self.assertTrue('<label for="id_captcha_1"' in str(r.content))

    def testRefreshView(self):
        r = self.client.get(reverse('captcha-refresh'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        try:
            new_data = json.loads(six.text_type(r.content, encoding='ascii'))
            self.assertTrue('image_url' in new_data)
        except:
            self.fail()

    def testContentLength(self):
        for key in [store.hashkey for store in six.itervalues(self.stores)]:
            response = self.client.get(reverse('captcha-image', kwargs=dict(key=key)))
            self.assertTrue(response.has_header('content-length'))
            self.assertTrue(response['content-length'].isdigit())
            self.assertTrue(int(response['content-length']))

    def testIssue12ProperInstantiation(self):
        """
        This test covers a default django field and widget behavior
        It not assert anything. If something is wrong it will raise a error!
        """
        settings.CAPTCHA_OUTPUT_FORMAT = u'%(image)s %(hidden_field)s %(text_field)s'
        widget = CaptchaTextInput(attrs={'class': 'required'})
        CaptchaField(widget=widget)

    def testTestMode_Issue15(self):
        __current_test_mode_setting  = settings.CAPTCHA_TEST_MODE
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


def trivial_challenge():
    return 'trivial', 'trivial'
