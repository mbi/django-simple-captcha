import os
import warnings

from django.conf import settings


CAPTCHA_FONT_PATH = getattr(
    settings,
    "CAPTCHA_FONT_PATH",
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "fonts/Vera.ttf")),
)
CAPTCHA_FONT_SIZE = getattr(settings, "CAPTCHA_FONT_SIZE", 22)
CAPTCHA_LETTER_ROTATION = getattr(settings, "CAPTCHA_LETTER_ROTATION", (-35, 35))
CAPTCHA_BACKGROUND_COLOR = getattr(settings, "CAPTCHA_BACKGROUND_COLOR", "#ffffff")
CAPTCHA_FOREGROUND_COLOR = getattr(settings, "CAPTCHA_FOREGROUND_COLOR", "#001100")
CAPTCHA_CHALLENGE_FUNCT = getattr(
    settings, "CAPTCHA_CHALLENGE_FUNCT", "captcha.helpers.random_char_challenge"
)
CAPTCHA_NOISE_FUNCTIONS = getattr(
    settings,
    "CAPTCHA_NOISE_FUNCTIONS",
    ("captcha.helpers.noise_arcs", "captcha.helpers.noise_dots"),
)
CAPTCHA_FILTER_FUNCTIONS = getattr(
    settings, "CAPTCHA_FILTER_FUNCTIONS", ("captcha.helpers.post_smooth",)
)
CAPTCHA_WORDS_DICTIONARY = getattr(
    settings, "CAPTCHA_WORDS_DICTIONARY", "/usr/share/dict/words"
)
CAPTCHA_PUNCTUATION = getattr(settings, "CAPTCHA_PUNCTUATION", """_"',.;:-""")
CAPTCHA_FLITE_PATH = getattr(settings, "CAPTCHA_FLITE_PATH", None)
CAPTCHA_SOX_PATH = getattr(settings, "CAPTCHA_SOX_PATH", None)
CAPTCHA_TIMEOUT = getattr(settings, "CAPTCHA_TIMEOUT", 5)  # Minutes
CAPTCHA_LENGTH = int(getattr(settings, "CAPTCHA_LENGTH", 4))  # Chars
# CAPTCHA_IMAGE_BEFORE_FIELD = getattr(settings, 'CAPTCHA_IMAGE_BEFORE_FIELD', True)
CAPTCHA_DICTIONARY_MIN_LENGTH = getattr(settings, "CAPTCHA_DICTIONARY_MIN_LENGTH", 0)
CAPTCHA_DICTIONARY_MAX_LENGTH = getattr(settings, "CAPTCHA_DICTIONARY_MAX_LENGTH", 99)
CAPTCHA_IMAGE_SIZE = getattr(settings, "CAPTCHA_IMAGE_SIZE", None)
CAPTCHA_IMAGE_TEMPLATE = getattr(
    settings, "CAPTCHA_IMAGE_TEMPLATE", "captcha/image.html"
)
CAPTCHA_HIDDEN_FIELD_TEMPLATE = getattr(
    settings, "CAPTCHA_HIDDEN_FIELD_TEMPLATE", "captcha/hidden_field.html"
)
CAPTCHA_TEXT_FIELD_TEMPLATE = getattr(
    settings, "CAPTCHA_TEXT_FIELD_TEMPLATE", "captcha/text_field.html"
)

if getattr(settings, "CAPTCHA_FIELD_TEMPLATE", None):
    msg = "CAPTCHA_FIELD_TEMPLATE setting is deprecated in favor of widget's template_name."
    warnings.warn(msg, DeprecationWarning)
CAPTCHA_FIELD_TEMPLATE = getattr(settings, "CAPTCHA_FIELD_TEMPLATE", None)
if getattr(settings, "CAPTCHA_OUTPUT_FORMAT", None):
    msg = "CAPTCHA_OUTPUT_FORMAT setting is deprecated in favor of widget's template_name."
    warnings.warn(msg, DeprecationWarning)
CAPTCHA_OUTPUT_FORMAT = getattr(settings, "CAPTCHA_OUTPUT_FORMAT", None)

CAPTCHA_MATH_CHALLENGE_OPERATOR = getattr(
    settings, "CAPTCHA_MATH_CHALLENGE_OPERATOR", "*"
)
CAPTCHA_GET_FROM_POOL = getattr(settings, "CAPTCHA_GET_FROM_POOL", False)
CAPTCHA_GET_FROM_POOL_TIMEOUT = getattr(settings, "CAPTCHA_GET_FROM_POOL_TIMEOUT", 5)

CAPTCHA_TEST_MODE = getattr(settings, "CAPTCHA_TEST_MODE", False)

CAPTCHA_2X_IMAGE = getattr(settings, "CAPTCHA_2X_IMAGE", True)

# Failsafe
if CAPTCHA_DICTIONARY_MIN_LENGTH > CAPTCHA_DICTIONARY_MAX_LENGTH:
    CAPTCHA_DICTIONARY_MIN_LENGTH, CAPTCHA_DICTIONARY_MAX_LENGTH = (
        CAPTCHA_DICTIONARY_MAX_LENGTH,
        CAPTCHA_DICTIONARY_MIN_LENGTH,
    )


def _callable_from_string(string_or_callable):
    if callable(string_or_callable):
        return string_or_callable
    else:
        return getattr(
            __import__(".".join(string_or_callable.split(".")[:-1]), {}, {}, [""]),
            string_or_callable.split(".")[-1],
        )


def get_challenge(generator=None):
    return _callable_from_string(generator or CAPTCHA_CHALLENGE_FUNCT)


def noise_functions():
    if CAPTCHA_NOISE_FUNCTIONS:
        return map(_callable_from_string, CAPTCHA_NOISE_FUNCTIONS)
    return []


def filter_functions():
    if CAPTCHA_FILTER_FUNCTIONS:
        return map(_callable_from_string, CAPTCHA_FILTER_FUNCTIONS)
    return []
