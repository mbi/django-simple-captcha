from django.urls import include, re_path

from .views import (
    test,
    test_custom_error_message,
    test_custom_generator,
    test_id_prefix,
    test_model_form,
    test_non_required,
    test_per_form_format,
)


urlpatterns = [
    re_path(r"test/$", test, name="captcha-test"),
    re_path(r"test-modelform/$", test_model_form, name="captcha-test-model-form"),
    re_path(
        r"test2/$", test_custom_error_message, name="captcha-test-custom-error-message"
    ),
    re_path(r"test3/$", test_per_form_format, name="test_per_form_format"),
    re_path(r"custom-generator/$", test_custom_generator, name="test_custom_generator"),
    re_path(
        r"test-non-required/$", test_non_required, name="captcha-test-non-required"
    ),
    re_path(r"test-id-prefix/$", test_id_prefix, name="captcha-test-id-prefix"),
    re_path(r"", include("captcha.urls")),
]
