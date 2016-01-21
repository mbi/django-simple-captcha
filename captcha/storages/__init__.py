from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from ..conf import settings as captcha_settings


class InvalidStorageBackendError(ImproperlyConfigured):
    pass


def get_storage(storage_conf=None):
    conf = storage_conf or captcha_settings.CAPTCHA_STORAGE
    try:
        backend = conf['BACKEND']
        # Trying to import the given backend, in case it's a dotted path
        backend_cls = import_string(backend)
    except (KeyError, ImportError) as e:
        raise InvalidStorageBackendError("Could not find storage backend '%s': %s" % (
            backend, e))
    try:
        params = conf['PARAMS'].copy()
    except KeyError:
        params = {}
    return backend_cls(params)


storage = get_storage()
