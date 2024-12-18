import json
import os
import random
import secrets
import subprocess
import tempfile
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from ranged_response import RangedFileResponse

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponse

from captcha.conf import settings
from captcha.helpers import captcha_audio_url, captcha_image_url
from captcha.models import CaptchaStore


# Distance of the drawn text from the top of the captcha image
DISTANCE_FROM_TOP = 4


def getsize(font, text):
    if hasattr(font, "getbbox"):
        _top, _left, _right, _bottom = font.getbbox(text)
        return _right - _left, _bottom - _top
    elif hasattr(font, "getoffset"):
        return tuple([x + y for x, y in zip(font.getsize(text), font.getoffset(text))])
    else:
        return font.getsize(text)


def makeimg(size):
    if settings.CAPTCHA_BACKGROUND_COLOR == "transparent":
        image = Image.new("RGBA", size)
    else:
        image = Image.new("RGB", size, settings.CAPTCHA_BACKGROUND_COLOR)
    return image


def captcha_image(request, key, scale=1):
    if scale == 2 and not settings.CAPTCHA_2X_IMAGE:
        raise Http404
    try:
        store = CaptchaStore.objects.get(hashkey=key)
    except CaptchaStore.DoesNotExist:
        # HTTP 410 Gone status so that crawlers don't index these expired urls.
        return HttpResponse(status=410)

    random.seed(key)  # Do not generate different images for the same key

    text = store.challenge

    if isinstance(settings.CAPTCHA_FONT_PATH, str):
        fontpath = settings.CAPTCHA_FONT_PATH
    elif isinstance(settings.CAPTCHA_FONT_PATH, (list, tuple)):
        fontpath = random.choice(settings.CAPTCHA_FONT_PATH)
    else:
        raise ImproperlyConfigured(
            "settings.CAPTCHA_FONT_PATH needs to be a path to a font or list of paths to fonts"
        )

    if fontpath.lower().strip().endswith("ttf"):
        font = ImageFont.truetype(fontpath, settings.CAPTCHA_FONT_SIZE * scale)
    else:
        font = ImageFont.load(fontpath)

    if settings.CAPTCHA_IMAGE_SIZE:
        size = settings.CAPTCHA_IMAGE_SIZE
    else:
        size = getsize(font, text)
        size = (size[0] * 2, int(size[1] * 1.4))

    image = makeimg(size)
    xpos = 2

    charlist = []
    for char in text:
        if char in settings.CAPTCHA_PUNCTUATION and len(charlist) >= 1:
            charlist[-1] += char
        else:
            charlist.append(char)

    for index, char in enumerate(charlist):
        fgimage = Image.new(
            "RGB", size, settings.get_letter_color(index, "".join(charlist))
        )
        charimage = Image.new("L", getsize(font, " %s " % char), "#000000")
        chardraw = ImageDraw.Draw(charimage)
        chardraw.text((0, 0), " %s " % char, font=font, fill="#ffffff")
        if settings.CAPTCHA_LETTER_ROTATION:
            charimage = charimage.rotate(
                random.randrange(*settings.CAPTCHA_LETTER_ROTATION),
                expand=0,
                resample=Image.BICUBIC,
            )
        charimage = charimage.crop(charimage.getbbox())
        maskimage = Image.new("L", size)

        maskimage.paste(
            charimage,
            (
                xpos,
                DISTANCE_FROM_TOP,
                xpos + charimage.size[0],
                DISTANCE_FROM_TOP + charimage.size[1],
            ),
        )
        size = maskimage.size
        image = Image.composite(fgimage, image, maskimage)
        xpos = xpos + 2 + charimage.size[0]

    if settings.CAPTCHA_IMAGE_SIZE:
        # centering captcha on the image
        tmpimg = makeimg(size)
        tmpimg.paste(
            image,
            (
                int((size[0] - xpos) / 2),
                int((size[1] - charimage.size[1]) / 2 - DISTANCE_FROM_TOP),
            ),
        )
        image = tmpimg.crop((0, 0, size[0], size[1]))
    else:
        image = image.crop((0, 0, xpos + 1, size[1]))
    draw = ImageDraw.Draw(image)

    for f in settings.noise_functions():
        draw = f(draw, image)
    for f in settings.filter_functions():
        image = f(image)

    out = BytesIO()
    image.save(out, "PNG")
    out.seek(0)

    response = HttpResponse(content_type="image/png")
    response.write(out.read())
    response["Content-length"] = out.tell()

    # At line :50 above we fixed the random seed so that we always generate the
    # same image, see: https://github.com/mbi/django-simple-captcha/pull/194
    # This is a problem though, because knowledge of the seed will let an attacker
    # predict the next random (globally). We therefore reset the random here.
    # Reported in https://github.com/mbi/django-simple-captcha/pull/221
    random.seed()

    return response


def captcha_audio(request, key):
    if settings.CAPTCHA_FLITE_PATH:
        try:
            store = CaptchaStore.objects.get(hashkey=key)
        except CaptchaStore.DoesNotExist:
            # HTTP 410 Gone status so that crawlers don't index these expired urls.
            return HttpResponse(status=410)

        text = store.challenge
        if "captcha.helpers.math_challenge" == settings.CAPTCHA_CHALLENGE_FUNCT:
            text = text.replace("*", "times").replace("-", "minus").replace("+", "plus")
        else:
            text = ", ".join(list(text))
        path = str(
            os.path.join(tempfile.gettempdir(), f"{key}_{secrets.token_urlsafe(6)}.wav")
        )
        subprocess.run([settings.CAPTCHA_FLITE_PATH, "-t", text, "-o", path])

        # Add arbitrary noise if sox is installed
        if settings.CAPTCHA_SOX_PATH:
            try:
                sample_rate = (
                    subprocess.run(
                        [settings.CAPTCHA_SOX_PATH, "--i", "-r", path],
                        capture_output=True,
                    )
                    .stdout.decode()
                    .strip()
                )

            except Exception:
                sample_rate = "8000"

            arbnoisepath = str(
                os.path.join(
                    tempfile.gettempdir(),
                    f"{key}_{secrets.token_urlsafe(6)}_noise.wav",
                )
            )
            subprocess.run(
                [
                    settings.CAPTCHA_SOX_PATH,
                    "-r",
                    sample_rate,
                    "-n",
                    arbnoisepath,
                    "synth",
                    "2",
                    "brownnoise",
                    "gain",
                    "-15",
                ]
            )
            mergedpath = str(
                os.path.join(
                    tempfile.gettempdir(),
                    f"{key}_{secrets.token_urlsafe(6)}_merged.wav",
                )
            )
            subprocess.run(
                [
                    settings.CAPTCHA_SOX_PATH,
                    "-m",
                    arbnoisepath,
                    path,
                    "-t",
                    "wavpcm",
                    "-b",
                    "16",
                    mergedpath,
                ]
            )
            os.remove(arbnoisepath)
            os.remove(path)
            os.rename(mergedpath, path)

        if os.path.isfile(path):
            # Move the response file to a filelike that will be deleted on close
            temporary_file = tempfile.TemporaryFile()
            with open(path, "rb") as original_file:
                temporary_file.write(original_file.read())
            temporary_file.seek(0)
            os.remove(path)

            response = RangedFileResponse(
                request, temporary_file, content_type="audio/wav"
            )
            response["Content-Disposition"] = 'attachment; filename="{}.wav"'.format(
                key
            )
            return response
    raise Http404


def captcha_refresh(request):
    """Return json with new captcha for ajax refresh request"""
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        raise Http404

    new_key = CaptchaStore.pick()
    to_json_response = {
        "key": new_key,
        "image_url": captcha_image_url(new_key),
        "audio_url": captcha_audio_url(new_key)
        if settings.CAPTCHA_FLITE_PATH
        else None,
    }
    return HttpResponse(json.dumps(to_json_response), content_type="application/json")
