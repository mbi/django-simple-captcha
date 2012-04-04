import os
from django.conf import settings

CAPTCHA_FONT_PATH = getattr(settings,'CAPTCHA_FONT_PATH', os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'fonts/Vera.ttf'))) 
CAPTCHA_FONT_SIZE = getattr(settings,'CAPTCHA_FONT_SIZE', 22)
CAPTCHA_LETTER_ROTATION = getattr(settings, 'CAPTCHA_LETTER_ROTATION', (-35,35))
CAPTCHA_BACKGROUND_COLOR = getattr(settings,'CAPTCHA_BACKGROUND_COLOR', '#ffffff')
CAPTCHA_FOREGROUND_COLOR= getattr(settings,'CAPTCHA_FOREGROUND_COLOR', '#001100')
CAPTCHA_CHALLENGE_FUNCT = getattr(settings,'CAPTCHA_CHALLENGE_FUNCT','captcha.helpers.random_char_challenge')
CAPTCHA_NOISE_FUNCTIONS = getattr(settings,'CAPTCHA_NOISE_FUNCTIONS', ('captcha.helpers.noise_arcs','captcha.helpers.noise_dots',))
CAPTCHA_FILTER_FUNCTIONS = getattr(settings,'CAPTCHA_FILTER_FUNCTIONS',('captcha.helpers.post_smooth',))
CAPTCHA_WORDS_DICTIONARY = getattr(settings,'CAPTCHA_WORDS_DICTIONARY', '/usr/share/dict/words')
CAPTCHA_PUNCTUATION = getattr(settings, 'CAPTCHA_PUNCTUATION', '''_"',.;:-''')
CAPTCHA_FLITE_PATH = getattr(settings,'CAPTCHA_FLITE_PATH',None)
CAPTCHA_TIMEOUT = getattr(settings, 'CAPTCHA_TIMEOUT', 5) # Minutes
CAPTCHA_LENGTH = int(getattr(settings, 'CAPTCHA_LENGTH', 4)) # Chars
CAPTCHA_IMAGE_BEFORE_FIELD = getattr(settings,'CAPTCHA_IMAGE_BEFORE_FIELD', True)
CAPTCHA_DICTIONARY_MIN_LENGTH = getattr(settings,'CAPTCHA_DICTIONARY_MIN_LENGTH', 0)
CAPTCHA_DICTIONARY_MAX_LENGTH = getattr(settings,'CAPTCHA_DICTIONARY_MAX_LENGTH', 99)
if CAPTCHA_IMAGE_BEFORE_FIELD:
    CAPTCHA_OUTPUT_FORMAT = getattr(settings,'CAPTCHA_OUTPUT_FORMAT', u'%(image)s %(hidden_field)s %(text_field)s')
else:
    CAPTCHA_OUTPUT_FORMAT = getattr(settings,'CAPTCHA_OUTPUT_FORMAT', u'%(hidden_field)s %(text_field)s %(image)s')


# Failsafe
if CAPTCHA_DICTIONARY_MIN_LENGTH > CAPTCHA_DICTIONARY_MAX_LENGTH:
    CAPTCHA_DICTIONARY_MIN_LENGTH, CAPTCHA_DICTIONARY_MAX_LENGTH = CAPTCHA_DICTIONARY_MAX_LENGTH, CAPTCHA_DICTIONARY_MIN_LENGTH


def _callable_from_string(string_or_callable):
    if callable(string_or_callable):
        return string_or_callable
    else:
        return getattr(__import__( '.'.join(string_or_callable.split('.')[:-1]), {}, {}, ['']), string_or_callable.split('.')[-1])
    
def get_challenge():
    return _callable_from_string(CAPTCHA_CHALLENGE_FUNCT)


def noise_functions():
    if CAPTCHA_NOISE_FUNCTIONS:
        return map(_callable_from_string, CAPTCHA_NOISE_FUNCTIONS)
    return list()

def filter_functions():
    if CAPTCHA_FILTER_FUNCTIONS:
        return map(_callable_from_string, CAPTCHA_FILTER_FUNCTIONS)
    return list()

