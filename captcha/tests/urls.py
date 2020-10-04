import django
from .views import (
    test,
    test_model_form,
    test_custom_error_message,
    test_per_form_format,
    test_non_required,
    test_id_prefix,
    test_custom_generator,
)

if django.VERSION >= (3, 1, 0):
    from django.urls import re_path as url, include
else:
    from django.conf.urls import url, include


urlpatterns = [
    url(r"test/$", test, name="captcha-test"),
    url(r"test-modelform/$", test_model_form, name="captcha-test-model-form"),
    url(r"test2/$", test_custom_error_message, name="captcha-test-custom-error-message"),
    url(r"test3/$", test_per_form_format, name="test_per_form_format"),
    url(r"custom-generator/$", test_custom_generator, name="test_custom_generator"),
    url(r"test-non-required/$", test_non_required, name="captcha-test-non-required"),
    url(r"test-id-prefix/$", test_id_prefix, name="captcha-test-id-prefix"),
    url(r"", include("captcha.urls")),
]
