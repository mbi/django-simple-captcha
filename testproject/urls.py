import django

if django.VERSION >= (3, 1, 0):
    from django.urls import re_path as url, include
else:
    from django.conf.urls import url, include

from .views import home

urlpatterns = [url(r"^$", home), url(r"^captcha/", include("captcha.urls"))]
