import os

from django.conf import settings
from django.utils.module_loading import import_string


CAPTCHA_FONT_PATH = getattr(
    settings,
    "CAPTCHA_FONT_PATH",
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "fonts/Vera.ttf")),
)
CAPTCHA_FONT_SIZE = getattr(settings, "CAPTCHA_FONT_SIZE", 22)
CAPTCHA_LETTER_ROTATION = getattr(settings, "CAPTCHA_LETTER_ROTATION", (-35, 35))
CAPTCHA_BACKGROUND_COLOR = getattr(settings, "CAPTCHA_BACKGROUND_COLOR", "#ffffff")
CAPTCHA_FOREGROUND_COLOR = getattr(settings, "CAPTCHA_FOREGROUND_COLOR", "#001100")
CAPTCHA_LETTER_COLOR_FUNCT = getattr(settings, "CAPTCHA_LETTER_COLOR_FUNCT", None)
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
    elif isinstance(string_or_callable, str):
        return import_string(string_or_callable)


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


def get_letter_color(index, challenge):
    if CAPTCHA_LETTER_COLOR_FUNCT:
        return _callable_from_string(CAPTCHA_LETTER_COLOR_FUNCT)(index, challenge)
    return CAPTCHA_FOREGROUND_COLOR
