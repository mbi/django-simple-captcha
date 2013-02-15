from cStringIO import StringIO
from captcha.conf import settings
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import simplejson as json
import random
import re
import tempfile
import os
import subprocess


try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import Image
    import ImageDraw
    import ImageFont

NON_DIGITS_RX = re.compile('[^\d]')


def captcha_image(request, key):
    store = get_object_or_404(CaptchaStore, hashkey=key)
    text = store.challenge

    if settings.CAPTCHA_FONT_PATH.lower().strip().endswith('ttf'):
        font = ImageFont.truetype(settings.CAPTCHA_FONT_PATH, settings.CAPTCHA_FONT_SIZE)
    else:
        font = ImageFont.load(settings.CAPTCHA_FONT_PATH)

    size = font.getsize(text)
    size = (size[0] * 2, int(size[1] * 1.2))
    image = Image.new('RGB', size, settings.CAPTCHA_BACKGROUND_COLOR)

    try:
        PIL_VERSION = int(NON_DIGITS_RX.sub('', Image.VERSION))
    except:
        PIL_VERSION = 116
    xpos = 2

    charlist = []
    for char in text:
        if char in settings.CAPTCHA_PUNCTUATION and len(charlist) >= 1:
            charlist[-1] += char
        else:
            charlist.append(char)
    for char in charlist:
        fgimage = Image.new('RGB', size, settings.CAPTCHA_FOREGROUND_COLOR)
        charimage = Image.new('L', font.getsize(' %s ' % char), '#000000')
        chardraw = ImageDraw.Draw(charimage)
        chardraw.text((0, 0), ' %s ' % char, font=font, fill='#ffffff')
        if settings.CAPTCHA_LETTER_ROTATION:
            if PIL_VERSION >= 116:
                charimage = charimage.rotate(random.randrange(*settings.CAPTCHA_LETTER_ROTATION), expand=0, resample=Image.BICUBIC)
            else:
                charimage = charimage.rotate(random.randrange(*settings.CAPTCHA_LETTER_ROTATION), resample=Image.BICUBIC)
        charimage = charimage.crop(charimage.getbbox())
        maskimage = Image.new('L', size)

        maskimage.paste(charimage, (xpos, 4, xpos + charimage.size[0], 4 + charimage.size[1]))
        size = maskimage.size
        image = Image.composite(fgimage, image, maskimage)
        xpos = xpos + 2 + charimage.size[0]

    image = image.crop((0, 0, xpos + 1, size[1]))
    draw = ImageDraw.Draw(image)

    for f in settings.noise_functions():
        draw = f(draw, image)
    for f in settings.filter_functions():
        image = f(image)

    out = StringIO()
    image.save(out, "PNG")
    out.seek(0)

    response = HttpResponse(content_type='image/png')
    response.write(out.read())
    response['Content-length'] = out.tell()

    return response


def captcha_audio(request, key):
    if settings.CAPTCHA_FLITE_PATH:
        store = get_object_or_404(CaptchaStore, hashkey=key)
        text = store.challenge
        if 'captcha.helpers.math_challenge' == settings.CAPTCHA_CHALLENGE_FUNCT:
            text = text.replace('*', 'times').replace('-', 'minus')
        else:
            text = ', '.join(list(text))
        path = str(os.path.join(tempfile.gettempdir(), '%s.wav' % key))
        subprocess.call([settings.CAPTCHA_FLITE_PATH, "-t", text, "-o", path])
        if os.path.isfile(path):
            response = HttpResponse()
            f = open(path, 'rb')
            response['Content-Type'] = 'audio/x-wav'
            response.write(f.read())
            f.close()
            os.unlink(path)
            return response
    raise Http404


def captcha_refresh(request):
    """  Return json with new captcha for ajax refresh request """
    if request.is_ajax():
        to_json_responce = dict()

        new_key = CaptchaStore.generate_key()
        to_json_responce['key'] = new_key
        to_json_responce['image_url'] = captcha_image_url(new_key)

        return HttpResponse(json.dumps(to_json_responce), content_type='application/json')
    raise Http404
