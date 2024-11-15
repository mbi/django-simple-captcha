from django.urls import include
from django.urls import re_path as url

from .views import home


urlpatterns = [
    url(r"^$", home),
    url(r"^captcha/", include("captcha.urls")),
]
