from django.conf.urls.defaults import *
urlpatterns = patterns('',
    url(r'test/$','captcha.tests.views.test',name='captcha-test'),
    url(r'test2/$','captcha.tests.views.test_custom_error_message',name='captcha-test-custom-error-message'),
    url(r'test3/$','captcha.tests.views.test_per_form_format', name='test_per_form_format'),
    url(r'',include('captcha.urls')),
)
