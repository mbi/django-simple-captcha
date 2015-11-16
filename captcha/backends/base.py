from captcha.conf import settings as captcha_settings


class DoesNotExist(Exception):
    """ Can't find captcha in store """
    pass


class BaseStore(object):
    DoesNotExist = DoesNotExist

    def generate_key(self):
        """
        Generate captcha with unique key
        """
        return captcha_settings.get_challenge()()

    def remove_expired(self):
        """
        Remove expired captcha records
        """
        pass

    def get(self, response=None, hashkey=None, allow_expired=True):
        """
        Get captcha from store, or rise exception if captcha wasn't found
        """
        pass
