try:
    from django.conf.urls import url, patterns, include
except ImportError:
    from django.conf.urls.defaults import url, patterns, include

urlpatterns = patterns('',
    url(r'test/$','captcha.tests.views.test',name='captcha-test'),
    url(r'test2/$','captcha.tests.views.test_custom_error_message',name='captcha-test-custom-error-message'),
    url(r'test3/$','captcha.tests.views.test_per_form_format', name='test_per_form_format'),
    url(r'',include('captcha.urls')),
)
