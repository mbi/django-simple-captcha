import random
from typing import Literal

from django.urls import reverse
from PIL.Image import Image as ImageType

from captcha.conf import settings


def math_challenge() -> tuple[str, str]:
    operators = ("+", "*", "-")
    operands: tuple[int, int] = (random.randint(1, 10), random.randint(1, 10))
    operator: Literal["+", "*", "-"] = random.choice(operators)

    if operands[0] < operands[1] and "-" == operator:
        operands = (operands[1], operands[0])

    challenge = "%d%s%d" % (operands[0], operator, operands[1])

    return (
        "{}=".format(challenge.replace("*", settings.CAPTCHA_MATH_CHALLENGE_OPERATOR)),
        str(eval(challenge)),
    )


def random_char_challenge() -> tuple[str, str]:
    chars, ret = "abcdefghijklmnopqrstuvwxyz", ""
    for _ in range(settings.CAPTCHA_LENGTH):
        ret += random.choice(chars)
    return ret.upper(), ret


def unicode_challenge() -> tuple[str, str]:
    chars, ret = "äàáëéèïíîöóòüúù", ""
    for i in range(settings.CAPTCHA_LENGTH):
        ret += random.choice(chars)
    return ret.upper(), ret


def word_challenge() -> tuple[str, str]:
    with open(settings.CAPTCHA_WORDS_DICTIONARY, "r") as fd:
        lines = fd.readlines()

    while True:
        word: str = random.choice(lines).strip()
        if (
            len(word) >= settings.CAPTCHA_DICTIONARY_MIN_LENGTH
            and len(word) <= settings.CAPTCHA_DICTIONARY_MAX_LENGTH
        ):
            break

    return word.upper(), word.lower()


def huge_words_and_punctuation_challenge() -> tuple[str, str]:
    "Yay, undocumneted. Mostly used to test Issue 39 - http://code.google.com/p/django-simple-captcha/issues/detail?id=39"
    with open(settings.CAPTCHA_WORDS_DICTIONARY, "rb") as fd:
        lines = fd.readlines()

    word = ""

    while True:
        word1 = random.choice(lines).strip()
        word2 = random.choice(lines).strip()
        punct = random.choice(settings.CAPTCHA_PUNCTUATION)
        word = "%s%s%s" % (word1, punct, word2)
        if (
            len(word) >= settings.CAPTCHA_DICTIONARY_MIN_LENGTH
            and len(word) <= settings.CAPTCHA_DICTIONARY_MAX_LENGTH
        ):
            break

    return word.upper(), word.lower()


def noise_arcs(draw, image: ImageType):
    size: tuple[int, int] = image.size
    draw.arc([-20, -20, size[0], 20], 0, 295, fill=settings.CAPTCHA_FOREGROUND_COLOR)
    draw.line(
        [-20, 20, size[0] + 20, size[1] - 20], fill=settings.CAPTCHA_FOREGROUND_COLOR
    )
    draw.line([-20, 0, size[0] + 20, size[1]], fill=settings.CAPTCHA_FOREGROUND_COLOR)
    return draw


def noise_dots(draw, image: ImageType):
    size: tuple[int, int] = image.size

    for _ in range(int(size[0] * size[1] * 0.1)):
        draw.point(
            (random.randint(0, size[0]), random.randint(0, size[1])),
            fill=settings.CAPTCHA_FOREGROUND_COLOR,
        )

    return draw


def noise_null(draw, image: ImageType):
    return draw


def post_smooth(image: ImageType) -> ImageType:
    from PIL import ImageFilter

    return image.filter(ImageFilter.SMOOTH)


def captcha_image_url(key) -> str:
    """Return url to image. Need for ajax refresh and, etc"""
    return reverse("captcha-image", args=[key])


def captcha_audio_url(key) -> str:
    """Return url to image. Need for ajax refresh and, etc"""
    return reverse("captcha-audio", args=[key])
