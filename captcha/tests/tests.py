import datetime
import json
import os
import re
from io import BytesIO

from PIL import Image
from testfixtures import LogCapture

import django
from django.core import management
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy

from captcha.conf import settings
from captcha.models import CaptchaStore


@override_settings(ROOT_URLCONF="captcha.tests.urls")
class CaptchaCase(TestCase):
    def setUp(self):
        self.stores = {}
        self.__current_settings_dictionary = settings.CAPTCHA_WORDS_DICTIONARY
        self.__current_settings_punctuation = settings.CAPTCHA_PUNCTUATION

        tested_helpers = [
            "captcha.helpers.math_challenge",
            "captcha.helpers.random_char_challenge",
            "captcha.helpers.unicode_challenge",
        ]
        if os.path.exists("/usr/share/dict/words"):
            settings.CAPTCHA_WORDS_DICTIONARY = "/usr/share/dict/words"
            settings.CAPTCHA_PUNCTUATION = ";-,."
            tested_helpers.append("captcha.helpers.word_challenge")
            tested_helpers.append(
                "captcha.helpers.huge_words_and_punctuation_challenge"
            )
        for helper in tested_helpers:
            challenge, response = settings._callable_from_string(helper)()
            (
                self.stores[helper.rsplit(".", 1)[-1].replace("_challenge", "_store")],
                _,
            ) = CaptchaStore.objects.get_or_create(
                challenge=challenge, response=response
            )
        challenge, response = settings.get_challenge()()
        self.stores["default_store"], _ = CaptchaStore.objects.get_or_create(
            challenge=challenge, response=response
        )
        self.default_store = self.stores["default_store"]

    def tearDown(self):
        settings.CAPTCHA_WORDS_DICTIONARY = self.__current_settings_dictionary
        settings.CAPTCHA_PUNCTUATION = self.__current_settings_punctuation

    def _assertFormError(self, response, form_name, *args, **kwargs):
        if django.VERSION >= (4, 1):
            self.assertFormError(response.context.get(form_name), *args, **kwargs)
        else:
            self.assertFormError(response, form_name, *args, **kwargs)

    def __extract_hash_and_response(self, r):
        hash_ = re.findall(r'value="([0-9a-f]+)"', str(r.content))[0]
        response = CaptchaStore.objects.get(hashkey=hash_).response
        return hash_, response

    def test_image(self):
        for key in [store.hashkey for store in self.stores.values()]:
            response = self.client.get(reverse("captcha-image", kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.has_header("content-type"))
            self.assertEqual(response["content-type"], "image/png")

    def test_audio(self):
        if not settings.CAPTCHA_FLITE_PATH:
            return
        for key in (
            self.stores.get("math_store").hashkey,
            self.stores.get("math_store").hashkey,
            self.default_store.hashkey,
        ):
            response = self.client.get(reverse("captcha-audio", kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.ranged_file.size > 1024)
            self.assertTrue(response.has_header("content-type"))
            self.assertEqual(response["content-type"], "audio/wav")

    def test_form_submit(self):
        r = self.client.get(reverse("captcha-test"))
        self.assertEqual(r.status_code, 200)
        hash_, response = self.__extract_hash_and_response(r)

        r = self.client.post(
            reverse("captcha-test"),
            dict(
                captcha_0=hash_,
                captcha_1=response,
                subject="xxx",
                sender="asasd@asdasd.com",
            ),
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(str(r.content).find("Form validated") > 0)

        r = self.client.post(
            reverse("captcha-test"),
            dict(
                captcha_0=hash_,
                captcha_1=response,
                subject="xxx",
                sender="asasd@asdasd.com",
            ),
        )
        self.assertEqual(r.status_code, 200)
        self.assertFalse(str(r.content).find("Form validated") > 0)

    def test_modelform(self):
        r = self.client.get(reverse("captcha-test-model-form"))
        self.assertEqual(r.status_code, 200)
        hash_, response = self.__extract_hash_and_response(r)

        r = self.client.post(
            reverse("captcha-test-model-form"),
            dict(
                captcha_0=hash_,
                captcha_1=response,
                subject="xxx",
                sender="asasd@asdasd.com",
            ),
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(str(r.content).find("Form validated") > 0)

        r = self.client.post(
            reverse("captcha-test-model-form"),
            dict(
                captcha_0=hash_,
                captcha_1=response,
                subject="xxx",
                sender="asasd@asdasd.com",
            ),
        )
        self.assertEqual(r.status_code, 200)
        self.assertFalse(str(r.content).find("Form validated") > 0)

    def test_wrong_submit(self):
        for urlname in ("captcha-test", "captcha-test-model-form"):
            r = self.client.get(reverse(urlname))
            self.assertEqual(r.status_code, 200)
            r = self.client.post(
                reverse(urlname),
                dict(
                    captcha_0="abc",
                    captcha_1="wrong response",
                    subject="xxx",
                    sender="asasd@asdasd.com",
                ),
            )
            self._assertFormError(r, "form", "captcha", gettext_lazy("Invalid CAPTCHA"))

    def test_deleted_expired(self):
        self.default_store.expiration = timezone.now() - datetime.timedelta(minutes=5)
        self.default_store.save()
        hash_ = self.default_store.hashkey
        r = self.client.post(
            reverse("captcha-test"),
            dict(
                captcha_0=hash_,
                captcha_1=self.default_store.response,
                subject="xxx",
                sender="asasd@asdasd.com",
            ),
        )

        self.assertEqual(r.status_code, 200)
        self.assertFalse("Form validated" in str(r.content))

        # expired -> deleted
        try:
            CaptchaStore.objects.get(hashkey=hash_)
            self.fail()
        except Exception:
            pass

    def test_custom_error_message(self):
        r = self.client.get(reverse("captcha-test-custom-error-message"))
        self.assertEqual(r.status_code, 200)
        # Wrong answer
        r = self.client.post(
            reverse("captcha-test-custom-error-message"),
            dict(captcha_0="abc", captcha_1="wrong response"),
        )
        self._assertFormError(r, "form", "captcha", "TEST CUSTOM ERROR MESSAGE")
        # empty answer
        r = self.client.post(
            reverse("captcha-test-custom-error-message"),
            dict(captcha_0="abc", captcha_1=""),
        )
        self._assertFormError(
            r, "form", "captcha", gettext_lazy("This field is required.")
        )

    def test_repeated_challenge(self):
        CaptchaStore.objects.create(challenge="xxx", response="xxx")
        try:
            CaptchaStore.objects.create(challenge="xxx", response="xxx")
        except Exception:
            self.fail()

    def test_repeated_challenge_form_submit(self):
        __current_challange_function = settings.CAPTCHA_CHALLENGE_FUNCT
        for urlname in ("captcha-test", "captcha-test-model-form"):
            settings.CAPTCHA_CHALLENGE_FUNCT = "captcha.tests.trivial_challenge"

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
            except Exception:
                self.fail()

            self.assertTrue(store_1.pk != store_2.pk)
            self.assertTrue(store_1.response == store_2.response)
            self.assertTrue(hash_1 != hash_2)

            r1 = self.client.post(
                reverse(urlname),
                dict(
                    captcha_0=hash_1,
                    captcha_1=store_1.response,
                    subject="xxx",
                    sender="asasd@asdasd.com",
                ),
            )
            self.assertEqual(r1.status_code, 200)
            self.assertTrue(str(r1.content).find("Form validated") > 0)

            try:
                store_2 = CaptchaStore.objects.get(hashkey=hash_2)
            except Exception:
                self.fail()

            r2 = self.client.post(
                reverse(urlname),
                dict(
                    captcha_0=hash_2,
                    captcha_1=store_2.response,
                    subject="xxx",
                    sender="asasd@asdasd.com",
                ),
            )
            self.assertEqual(r2.status_code, 200)
            self.assertTrue(str(r2.content).find("Form validated") > 0)
        settings.CAPTCHA_CHALLENGE_FUNCT = __current_challange_function

    def test_custom_generator(self):
        r = self.client.get(reverse("test_custom_generator"))
        hash_, response = self.__extract_hash_and_response(r)
        self.assertEqual(response, "111111")

    def test_refresh_view(self):
        r = self.client.get(
            reverse("captcha-refresh"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        try:
            new_data = json.loads(str(r.content, encoding="ascii"))
            self.assertTrue("image_url" in new_data)
            self.assertTrue("audio_url" in new_data)
        except Exception:
            self.fail()

    def test_content_length(self):
        for key in [store.hashkey for store in self.stores.values()]:
            response = self.client.get(reverse("captcha-image", kwargs=dict(key=key)))
            self.assertTrue(response.has_header("content-length"))
            self.assertTrue(response["content-length"].isdigit())
            self.assertTrue(int(response["content-length"]))

    def test_test_mode_issue15(self):
        __current_test_mode_setting = settings.CAPTCHA_TEST_MODE
        settings.CAPTCHA_TEST_MODE = False
        r = self.client.get(reverse("captcha-test"))
        self.assertEqual(r.status_code, 200)
        r = self.client.post(
            reverse("captcha-test"),
            dict(
                captcha_0="abc",
                captcha_1="wrong response",
                subject="xxx",
                sender="asasd@asdasd.com",
            ),
        )
        self._assertFormError(r, "form", "captcha", gettext_lazy("Invalid CAPTCHA"))

        settings.CAPTCHA_TEST_MODE = True
        # Test mode, only 'PASSED' is accepted
        r = self.client.get(reverse("captcha-test"))
        self.assertEqual(r.status_code, 200)
        r = self.client.post(
            reverse("captcha-test"),
            dict(
                captcha_0="abc",
                captcha_1="wrong response",
                subject="xxx",
                sender="asasd@asdasd.com",
            ),
        )
        self._assertFormError(r, "form", "captcha", gettext_lazy("Invalid CAPTCHA"))

        r = self.client.get(reverse("captcha-test"))
        self.assertEqual(r.status_code, 200)
        r = self.client.post(
            reverse("captcha-test"),
            dict(
                captcha_0="abc",
                captcha_1="passed",
                subject="xxx",
                sender="asasd@asdasd.com",
            ),
        )
        self.assertTrue(str(r.content).find("Form validated") > 0)
        settings.CAPTCHA_TEST_MODE = __current_test_mode_setting

    def test_get_version(self):
        import captcha

        captcha.get_version()

    def test_missing_value(self):
        r = self.client.get(reverse("captcha-test-non-required"))
        self.assertEqual(r.status_code, 200)
        hash_, response = self.__extract_hash_and_response(r)

        # Empty response is okay when required is False
        r = self.client.post(
            reverse("captcha-test-non-required"),
            dict(subject="xxx", sender="asasd@asdasd.com"),
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(str(r.content).find("Form validated") > 0)

        # But a valid response is okay, too
        r = self.client.get(reverse("captcha-test-non-required"))
        self.assertEqual(r.status_code, 200)
        hash_, response = self.__extract_hash_and_response(r)

        r = self.client.post(
            reverse("captcha-test-non-required"),
            dict(
                captcha_0=hash_,
                captcha_1=response,
                subject="xxx",
                sender="asasd@asdasd.com",
            ),
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(str(r.content).find("Form validated") > 0)

    def test_autocomplete_off(self):
        r = self.client.get(reverse("captcha-test"))
        captcha_input = (
            '<input type="text" name="captcha_1" autocomplete="off" '
            'spellcheck="false" autocorrect="off" '
            'autocapitalize="off" id="id_captcha_1" required />'
        )
        if django.VERSION >= (5, 0):
            captcha_input = (
                '<input type="text" name="captcha_1" autocomplete="off" '
                'spellcheck="false" autocorrect="off" '
                'autocapitalize="off" id="id_captcha_1" '
                "required />"
            )
        self.assertContains(r, captcha_input, html=True)

    def test_issue201_autocomplete_off_on_hiddeninput(self):
        r = self.client.get(reverse("captcha-test"))

        # Inspect the response context to find out the captcha key.
        key = r.context["form"]["captcha"].field.widget._key

        # Assety that autocomplete=off is set on the hidden captcha field.
        if django.VERSION >= (5, 0):
            self.assertInHTML(
                (
                    f'<input type="hidden" name="captcha_0" value="{key}" '
                    'id="id_captcha_0" autocomplete="off" '
                    "required />"
                ),
                str(r.content),
            )

        else:
            self.assertInHTML(
                (
                    f'<input type="hidden" name="captcha_0" value="{key}" '
                    'id="id_captcha_0" autocomplete="off" required />'
                ),
                str(r.content),
            )

    def test_transparent_background(self):
        __current_test_mode_setting = settings.CAPTCHA_BACKGROUND_COLOR
        settings.CAPTCHA_BACKGROUND_COLOR = "transparent"
        for key in [store.hashkey for store in self.stores.values()]:
            response = self.client.get(reverse("captcha-image", kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.has_header("content-type"))
            self.assertEqual(response["content-type"], "image/png")

        settings.CAPTCHA_BACKGROUND_COLOR = __current_test_mode_setting

    def test_expired_captcha_returns_410(self):
        for key in [store.hashkey for store in self.stores.values()]:
            response = self.client.get(reverse("captcha-image", kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            CaptchaStore.objects.filter(hashkey=key).delete()
            response = self.client.get(reverse("captcha-image", kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 410)

    def test_id_prefix(self):
        r = self.client.get(reverse("captcha-test-id-prefix"))
        self.assertTrue(
            '<label for="form1_id_captcha1_1">Captcha1:</label>' in str(r.content)
        )
        self.assertTrue('id="form1_id_captcha1_1"' in str(r.content))
        self.assertTrue(
            '<label for="form2_id_captcha2_1">Captcha2:</label>' in str(r.content)
        )
        self.assertTrue('id="form2_id_captcha2_1"' in str(r.content))

    def test_image_size(self):
        __current_test_mode_setting = settings.CAPTCHA_IMAGE_SIZE
        for key in [store.hashkey for store in self.stores.values()]:
            settings.CAPTCHA_IMAGE_SIZE = (201, 97)
            response = self.client.get(reverse("captcha-image", kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.has_header("content-type"))
            self.assertEqual(response["content-type"], "image/png")
            self.assertEqual(Image.open(BytesIO(response.content)).size, (201, 97))

        settings.CAPTCHA_IMAGE_SIZE = __current_test_mode_setting

    def test_multiple_fonts(self):
        vera = os.path.join(os.path.dirname(__file__), "..", "fonts", "Vera.ttf")
        __current_test_mode_setting = settings.CAPTCHA_FONT_PATH
        settings.CAPTCHA_FONT_PATH = vera

        for key in [store.hashkey for store in self.stores.values()]:
            response = self.client.get(reverse("captcha-image", kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["content-type"], "image/png")

        settings.CAPTCHA_FONT_PATH = [vera, vera, vera]
        for key in [store.hashkey for store in self.stores.values()]:
            response = self.client.get(reverse("captcha-image", kwargs=dict(key=key)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["content-type"], "image/png")

        settings.CAPTCHA_FONT_PATH = False
        for key in [store.hashkey for store in self.stores.values()]:
            try:
                response = self.client.get(
                    reverse("captcha-image", kwargs=dict(key=key))
                )
                self.fail()
            except ImproperlyConfigured:
                pass

        settings.CAPTCHA_FONT_PATH = __current_test_mode_setting

    def test_math_challenge(self):
        __current_test_mode_setting = settings.CAPTCHA_MATH_CHALLENGE_OPERATOR
        settings.CAPTCHA_MATH_CHALLENGE_OPERATOR = "~"
        helper = "captcha.helpers.math_challenge"
        challenge, response = settings._callable_from_string(helper)()

        while settings.CAPTCHA_MATH_CHALLENGE_OPERATOR not in challenge:
            challenge, response = settings._callable_from_string(helper)()

        self.assertEqual(
            response,
            str(
                eval(
                    challenge.replace(settings.CAPTCHA_MATH_CHALLENGE_OPERATOR, "*")[
                        :-1
                    ]
                )
            ),
        )
        settings.CAPTCHA_MATH_CHALLENGE_OPERATOR = __current_test_mode_setting

    def test_get_from_pool(self):
        __current_test_get_from_pool_setting = settings.CAPTCHA_GET_FROM_POOL
        __current_test_get_from_pool_timeout_setting = (
            settings.CAPTCHA_GET_FROM_POOL_TIMEOUT
        )
        __current_test_timeout_setting = settings.CAPTCHA_TIMEOUT
        settings.CAPTCHA_GET_FROM_POOL = True
        settings.CAPTCHA_GET_FROM_POOL_TIMEOUT = 5
        settings.CAPTCHA_TIMEOUT = 90
        CaptchaStore.objects.all().delete()  # Delete objects created during SetUp
        POOL_SIZE = 10
        CaptchaStore.create_pool(count=POOL_SIZE)
        self.assertEqual(CaptchaStore.objects.count(), POOL_SIZE)
        pool = CaptchaStore.objects.values_list("hashkey", flat=True)
        random_pick = CaptchaStore.pick()
        self.assertIn(random_pick, pool)
        # pick() should not create any extra captcha
        self.assertEqual(CaptchaStore.objects.count(), POOL_SIZE)
        settings.CAPTCHA_GET_FROM_POOL = __current_test_get_from_pool_setting
        settings.CAPTCHA_GET_FROM_POOL_TIMEOUT = (
            __current_test_get_from_pool_timeout_setting
        )
        settings.CAPTCHA_TIMEOUT = __current_test_timeout_setting

    def test_captcha_create_pool(self):
        CaptchaStore.objects.all().delete()  # Delete objects created during SetUp
        POOL_SIZE = 10
        management.call_command("captcha_create_pool", pool_size=POOL_SIZE, verbosity=0)
        self.assertEqual(CaptchaStore.objects.count(), POOL_SIZE)

    def test_empty_pool_fallback(self):
        __current_test_get_from_pool_setting = settings.CAPTCHA_GET_FROM_POOL
        settings.CAPTCHA_GET_FROM_POOL = True
        CaptchaStore.objects.all().delete()  # Delete objects created during SetUp
        with LogCapture() as log:
            CaptchaStore.pick()
        log.check(
            ("captcha.models", "ERROR", "Couldn't get a captcha from pool, generating")
        )
        self.assertEqual(CaptchaStore.objects.count(), 1)
        settings.CAPTCHA_GET_FROM_POOL = __current_test_get_from_pool_setting


def trivial_challenge():
    return "trivial", "trivial"
