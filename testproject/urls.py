try:
    from django.conf.urls import include, url
except ImportError:
    from django.conf.urls.defaults import include, url

from .views import home

urlpatterns = [
    url(r'^$', home),
    url(r'^captcha/', include('captcha.urls')),
]
