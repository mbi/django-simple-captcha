from django.urls import re_path

from captcha import views


urlpatterns = [
    re_path(
        r"image/(?P<key>\w+)/$",
        views.captcha_image,
        name="captcha-image",
        kwargs={"scale": 1},
    ),
    re_path(
        r"image/(?P<key>\w+)@2/$",
        views.captcha_image,
        name="captcha-image-2x",
        kwargs={"scale": 2},
    ),
    re_path(r"audio/(?P<key>\w+).wav$", views.captcha_audio, name="captcha-audio"),
    re_path(r"refresh/$", views.captcha_refresh, name="captcha-refresh"),
]
