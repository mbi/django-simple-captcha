# -*- coding: utf-8 -*-
from captcha.conf import settings
from captcha.models import CaptchaStore
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse

import datetime


class CaptchaCase(TestCase):
    urls = 'captcha.tests.urls'

    def setUp(self):
        self.default_challenge = settings.get_challenge()()
        self.math_challenge = settings._callable_from_string('captcha.helpers.math_challenge')()
        self.chars_challenge = settings._callable_from_string('captcha.helpers.random_char_challenge')()
        self.unicode_challenge = settings._callable_from_string('captcha.helpers.unicode_challenge')()
        
        self.default_store, created =  CaptchaStore.objects.get_or_create(challenge=self.default_challenge[0],response=self.default_challenge[1])
        self.math_store, created = CaptchaStore.objects.get_or_create(challenge=self.math_challenge[0],response=self.math_challenge[1])
        self.chars_store, created = CaptchaStore.objects.get_or_create(challenge=self.chars_challenge[0],response=self.chars_challenge[1])
        self.unicode_store, created = CaptchaStore.objects.get_or_create(challenge=self.unicode_challenge[0],response=self.unicode_challenge[1])
        
        
        

    def testImages(self):
        for key in (self.math_store.hashkey, self.chars_store.hashkey, self.default_store.hashkey, self.unicode_store.hashkey):
            response = self.client.get(reverse('captcha-image',kwargs=dict(key=key)))
            self.failUnlessEqual(response.status_code, 200)
            self.assertTrue(response.has_header('content-type'))
            self.assertEquals(response._headers.get('content-type'), ('Content-Type', 'image/png'))

    def testAudio(self):
        if not settings.CAPTCHA_FLITE_PATH:
            return
        for key in (self.math_store.hashkey, self.chars_store.hashkey, self.default_store.hashkey, self.unicode_store.hashkey):
            response = self.client.get(reverse('captcha-audio',kwargs=dict(key=key)))
            self.failUnlessEqual(response.status_code, 200)
            self.assertTrue(len(response.content) > 1024)
            self.assertTrue(response.has_header('content-type'))
            self.assertEquals(response._headers.get('content-type'), ('Content-Type', 'audio/x-wav'))
            
    def testFormSubmit(self):        
        r = self.client.get(reverse('captcha-test'))
        self.failUnlessEqual(r.status_code, 200)
        hash_ = r.content[r.content.find('value="')+7:r.content.find('value="')+47]
        try:
            response = CaptchaStore.objects.get(hashkey=hash_).response
        except:
            self.fail()
            
        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_,captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.failUnlessEqual(r.status_code, 200)
        self.assertTrue(r.content.find('Form validated') > 0)
        
        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_,captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.failUnlessEqual(r.status_code, 200)
        self.assertFalse(r.content.find('Form validated') > 0)


        
    def testWrongSubmit(self):        
        r = self.client.get(reverse('captcha-test'))
        self.failUnlessEqual(r.status_code, 200)
        r = self.client.post(reverse('captcha-test'), dict(captcha_0='abc',captcha_1='wrong response', subject='xxx', sender='asasd@asdasd.com'))
        self.assertFormError(r,'form','captcha',_('Invalid CAPTCHA'))

    def testDeleteExpired(self):
        self.default_store.expiration = datetime.datetime.now() - datetime.timedelta(minutes=5)
        self.default_store.save()
        hash_ = self.default_store.hashkey
        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_,captcha_1=self.default_store.response, subject='xxx', sender='asasd@asdasd.com'))
        
        self.failUnlessEqual(r.status_code, 200)
        self.assertFalse(r.content.find('Form validated') > 0)
        
        # expired -> deleted
        try:
            CaptchaStore.objects.get(hashkey=hash_)
            self.fail()
        except:
            pass
    
    def testCustomErrorMessage(self):
        r = self.client.get(reverse('captcha-test-custom-error-message'))
        self.failUnlessEqual(r.status_code, 200)
        
        # Wrong answer
        r = self.client.post(reverse('captcha-test-custom-error-message'), dict(captcha_0='abc',captcha_1='wrong response'))
        self.assertFormError(r,'form','captcha','TEST CUSTOM ERROR MESSAGE')
        # empty answer
        r = self.client.post(reverse('captcha-test-custom-error-message'), dict(captcha_0='abc',captcha_1=''))
        self.assertFormError(r,'form','captcha',_('This field is required.'))

    def testRepeatedChallenge(self):
        store = CaptchaStore.objects.create(challenge='xxx',response='xxx')
        try:
            store2 = CaptchaStore.objects.create(challenge='xxx',response='xxx')
        except Exception:
            self.fail()
        
        
    def testRepeatedChallengeFormSubmit(self):   
        settings.CAPTCHA_CHALLENGE_FUNCT = 'captcha.tests.trivial_challenge'     
        
        r1 = self.client.get(reverse('captcha-test'))
        r2 = self.client.get(reverse('captcha-test'))
        self.failUnlessEqual(r1.status_code, 200)
        self.failUnlessEqual(r2.status_code, 200)
        hash_1 = r1.content[r1.content.find('value="')+7:r1.content.find('value="')+47]
        hash_2 = r2.content[r2.content.find('value="')+7:r2.content.find('value="')+47]
        try:
            store_1 = CaptchaStore.objects.get(hashkey=hash_1)
            store_2 = CaptchaStore.objects.get(hashkey=hash_2)
        except:
            self.fail()
        
        self.assertTrue(store_1.pk != store_2.pk)
        self.assertTrue(store_1.response == store_2.response)
        self.assertTrue(hash_1 != hash_2)
        
        

        r1 = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_1,captcha_1=store_1.response, subject='xxx', sender='asasd@asdasd.com'))
        self.failUnlessEqual(r1.status_code, 200)
        self.assertTrue(r1.content.find('Form validated') > 0)
        
        try:
            store_2 = CaptchaStore.objects.get(hashkey=hash_2)
        except:
            self.fail()

        r2 = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_2,captcha_1=store_2.response, subject='xxx', sender='asasd@asdasd.com'))
        self.failUnlessEqual(r2.status_code, 200)
        self.assertTrue(r2.content.find('Form validated') > 0)

    def testOutputFormat(self):
        settings.CAPTCHA_OUTPUT_FORMAT =  u'%(image)s<p>Hello, captcha world</p>%(hidden_field)s%(text_field)s'
        r = self.client.get(reverse('captcha-test'))
        self.failUnlessEqual(r.status_code, 200)
        self.assertTrue('<p>Hello, captcha world</p>' in r.content)

    def testInvalidOutputFormat(self):
        settings.CAPTCHA_OUTPUT_FORMAT =  u'%(image)s'
        try:
            r = self.client.get(reverse('captcha-test'))
            self.fail()
        except ImproperlyConfigured,e:
            self.failUnless('CAPTCHA_OUTPUT_FORMAT' in unicode(e))

    def testPerFormFormat(self):
        settings.CAPTCHA_OUTPUT_FORMAT =  u'%(image)s testCustomFormatString %(hidden_field)s %(text_field)s'
        r = self.client.get(reverse('captcha-test'))
        self.failUnless('testCustomFormatString' in r.content)
        r = self.client.get(reverse('test_per_form_format'))
        self.failUnless('testPerFieldCustomFormatString' in r.content)

    def testIssue31ProperLabel(self):
        settings.CAPTCHA_OUTPUT_FORMAT =  u'%(image)s %(hidden_field)s %(text_field)s'
        r = self.client.get(reverse('captcha-test'))
        self.failUnless('<label for="id_captcha_1"' in r.content)
        


def trivial_challenge():
    return 'trivial','trivial'
