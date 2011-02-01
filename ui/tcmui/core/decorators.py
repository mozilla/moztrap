from functools import wraps

from .api import admin


def as_admin(method):
    """
    A decorator for methods of an api.RemoteObject that causes the method to be
    executed with admin permissions, without disturbing the credentials stored
    on the object itself.

    """
    @wraps(method)
    def _wrapped(self, *args, **kwargs):
        auth = self.auth
        self.auth = admin
        ret = method(self, *args, **kwargs)
        self.auth = auth
        return ret
    return _wrapped
