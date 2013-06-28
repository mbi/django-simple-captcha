try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('captcha.views',
    url(r'image/(?P<key>\w+)/$', 'captcha_image', name='captcha-image', kwargs={'scale': 1}),
    url(r'image/(?P<key>\w+)@2/$', 'captcha_image', name='captcha-image-2x', kwargs={'scale': 2}),
    url(r'audio/(?P<key>\w+)/$', 'captcha_audio', name='captcha-audio'),
    url(r'refresh/$', 'captcha_refresh', name='captcha-refresh'),
)
