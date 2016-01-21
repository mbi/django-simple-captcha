from django.core.cache import caches
from django.utils.encoding import force_text

from ..helpers import get_safe_now
from .base import BaseStorage


class CacheStorage(BaseStorage):
    key_pattern = "captcha_storage_cache_%s"

    def __init__(self, params):
        super(CacheStorage, self).__init__(params)
        alias = params.get('ALIAS', 'default')
        self.cache = caches[alias]

    def get_key(self, hashkey):
        return self.key_pattern % hashkey

    def create_obj(self, challenge, response, hashkey, expiration):
        key = self.get_key(hashkey)
        data = dict(
            challenge=force_text(challenge),
            response=force_text(response),
            hashkey=force_text(hashkey),
            expiration=expiration
        )
        self.cache.set(key, data, timeout=self.get_timeout())
        return self.model_class(**data)

    def delete(self, hashkey, obj=None):
        key = self.get_key(hashkey)
        self.cache.delete(key)

    def get(self, hashkey):
        key = self.get_key(hashkey)
        data = self.cache.get(key)
        if not data:
            raise self.model_class.DoesNotExist
        return self.model_class(**data)

    def get_timeout(self):
        return (self.get_expiration() - get_safe_now()).total_seconds()

    def remove_expired(self):
        """
        In cache keys expired automatically
        """
        pass

    def get_count_of_expired(self):
        """
        undefined for cache
        """
        return None
