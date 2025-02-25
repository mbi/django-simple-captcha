from django.conf import settings
from django.urls import include, re_path

from .views import (
    test,
    test_custom_error_message,
    test_custom_generator,
    test_id_prefix,
    test_model_form,
    test_non_required,
)


urlpatterns = [
    re_path(r"test/$", test, name="captcha-test"),
    re_path(r"test-modelform/$", test_model_form, name="captcha-test-model-form"),
    re_path(
        r"test2/$", test_custom_error_message, name="captcha-test-custom-error-message"
    ),
    re_path(r"custom-generator/$", test_custom_generator, name="test_custom_generator"),
    re_path(
        r"test-non-required/$", test_non_required, name="captcha-test-non-required"
    ),
    re_path(r"test-id-prefix/$", test_id_prefix, name="captcha-test-id-prefix"),
    re_path(r"", include("captcha.urls")),
]


if "rest_framework" in settings.INSTALLED_APPS:
    from .drf_views import test_model_serializer, test_serializer

    urlpatterns += [
        re_path(r"test-serializer/$", test_serializer, name="captcha-test-serializer"),
        re_path(
            r"test-model-serializer/$",
            test_model_serializer,
            name="captcha-test-model-serializer",
        ),
    ]
