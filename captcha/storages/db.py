from ..helpers import get_safe_now
from .base import BaseStorage


class DBStorage(BaseStorage):

    def create_obj(self, challenge, response, hashkey, expiration):
        return self.model_class.objects.create(
            challenge=challenge,
            response=response,
            hashkey=hashkey,
            expiration=expiration
        )

    def delete(self, hashkey, obj=None):
        if not obj:
            obj = self.get(hashkey)
        obj.delete()

    def get(self, hashkey):
        return self.model_class.objects.get(hashkey=hashkey)

    def expired_qs(self):
        return self.model_class.objects.filter(expiration__lte=get_safe_now())

    def remove_expired(self):
        self.expired_qs().delete()

    def get_count_of_expired(self):
        return self.expired_qs().count()
