import re

VERSION = (0, 4, 1)


def get_version(svn=False):
    "Returns the version as a human-format string."
    return '.'.join([str(i) for i in VERSION])


def pillow_required():
    def pil_version(version):
        try:
            return int(re.compile('[^\d]').sub('', version))
        except:
            return 116

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        try:
            import Image
            import ImageDraw
            import ImageFont
        except ImportError:
            return True

    return pil_version(Image.VERSION) < 116
