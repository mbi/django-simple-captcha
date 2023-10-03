from django.core.exceptions import ImproperlyConfigured
from django.forms import ValidationError
from django.forms.fields import CharField, MultiValueField
from django.forms.widgets import HiddenInput, MultiWidget, TextInput
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy

from captcha.conf import settings
from captcha.models import CaptchaStore


class CaptchaHiddenInput(HiddenInput):
    """Hidden input for the captcha key."""

    # Use *args and **kwargs because signature changed in Django 1.11
    def build_attrs(self, *args, **kwargs):
        """Disable autocomplete to prevent problems on page reload."""

        attrs = super().build_attrs(*args, **kwargs)
        attrs["autocomplete"] = "off"
        return attrs


class CaptchaAnswerInput(TextInput):
    """Text input for captcha answer."""

    # Use *args and **kwargs because signature changed in Django 1.11
    def build_attrs(self, *args, **kwargs):
        """Disable automatic corrections and completions."""
        attrs = super().build_attrs(*args, **kwargs)
        attrs["autocapitalize"] = "off"
        attrs["autocomplete"] = "off"
        attrs["autocorrect"] = "off"
        attrs["spellcheck"] = "false"
        return attrs


class BaseCaptchaTextInput(MultiWidget):
    """
    Base class for Captcha widgets
    """

    def __init__(self, attrs=None):
        widgets = (CaptchaHiddenInput(attrs), CaptchaAnswerInput(attrs))
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(",")
        return [None, None]

    def fetch_captcha_store(self, name, value, attrs=None, generator=None):
        """
        Fetches a new CaptchaStore
        This has to be called inside render
        """
        try:
            reverse("captcha-image", args=("dummy",))
        except NoReverseMatch:
            raise ImproperlyConfigured(
                "Make sure you've included captcha.urls as explained in the INSTALLATION section on http://readthedocs.org/docs/django-simple-captcha/en/latest/usage.html#installation"
            )

        if settings.CAPTCHA_GET_FROM_POOL:
            key = CaptchaStore.pick()
        else:
            key = CaptchaStore.generate_key(generator)

        # these can be used by format_output and render
        self._value = [key, ""]
        self._key = key
        self.id_ = self.build_attrs(attrs).get("id", None)

    def id_for_label(self, id_):
        if id_:
            return id_ + "_1"
        return id_

    def image_url(self):
        return reverse("captcha-image", kwargs={"key": self._key})

    def audio_url(self):
        return (
            reverse("captcha-audio", kwargs={"key": self._key})
            if settings.CAPTCHA_FLITE_PATH
            else None
        )

    def refresh_url(self):
        return reverse("captcha-refresh")


class CaptchaTextInput(BaseCaptchaTextInput):
    template_name = "captcha/widgets/captcha.html"

    def __init__(
        self,
        attrs=None,
        id_prefix=None,
        generator=None,
        # output_format=None,
    ):
        self.id_prefix = id_prefix
        self.generator = generator
        super().__init__(attrs)

    def build_attrs(self, *args, **kwargs):
        ret = super().build_attrs(*args, **kwargs)
        if self.id_prefix and "id" in ret:
            ret["id"] = "%s_%s" % (self.id_prefix, ret["id"])
        return ret

    def id_for_label(self, id_):
        ret = super().id_for_label(id_)
        if self.id_prefix and "id" in ret:
            ret = "%s_%s" % (self.id_prefix, ret)
        return ret

    def get_context(self, name, value, attrs):
        """Add captcha specific variables to context."""
        context = super().get_context(name, value, attrs)
        context["image"] = self.image_url()
        context["audio"] = self.audio_url()
        return context

    def format_output(self, rendered_widgets):
        # hidden_field, text_field = rendered_widgets
        if self.output_format:
            ret = self.output_format % {
                "image": self.image_and_audio,
                "hidden_field": self.hidden_field,
                "text_field": self.text_field,
            }
            return ret

    def render(self, name, value, attrs=None, renderer=None):
        self.fetch_captcha_store(name, value, attrs, self.generator)

        extra_kwargs = {}
        extra_kwargs["renderer"] = renderer

        return super().render(name, self._value, attrs=attrs, **extra_kwargs)


class CaptchaField(MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (CharField(show_hidden_initial=True), CharField())
        if "error_messages" not in kwargs or "invalid" not in kwargs.get(
            "error_messages"
        ):
            if "error_messages" not in kwargs:
                kwargs["error_messages"] = {}
            kwargs["error_messages"].update(
                {"invalid": gettext_lazy("Invalid CAPTCHA")}
            )

        kwargs["widget"] = kwargs.pop(
            "widget",
            CaptchaTextInput(
                id_prefix=kwargs.pop("id_prefix", None),
                generator=kwargs.pop("generator", None),
            ),
        )

        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return ",".join(data_list)
        return None

    def clean(self, value):
        super().clean(value)
        response, value[1] = (value[1] or "").strip().lower(), ""
        if not settings.CAPTCHA_GET_FROM_POOL:
            CaptchaStore.remove_expired()
        if settings.CAPTCHA_TEST_MODE and response.lower() == "passed":
            # automatically pass the test
            try:
                # try to delete the captcha based on its hash
                CaptchaStore.objects.get(hashkey=value[0]).delete()
            except CaptchaStore.DoesNotExist:
                # ignore errors
                pass
        elif not self.required and not response:
            pass
        else:
            try:
                CaptchaStore.objects.get(
                    response=response, hashkey=value[0], expiration__gt=timezone.now()
                ).delete()
            except CaptchaStore.DoesNotExist:
                raise ValidationError(
                    getattr(self, "error_messages", {}).get(
                        "invalid", gettext_lazy("Invalid CAPTCHA")
                    )
                )
        return value
