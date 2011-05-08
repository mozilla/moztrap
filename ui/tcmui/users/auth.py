from ..core.auth import Credentials
from .models import User



class UserCredentials(Credentials):
    """
    Expands the core Credentials object with a lazy ``user`` property.

    """
    def __init__(self, *args, **kwargs):
        super(UserCredentials, self).__init__(*args, **kwargs)
        self._user = None


    def _get_user(self):
        if self._user is None:
            try:
                user = User.current(auth=self, cache=False)
                user.deliver()
            except (User.Forbidden, User.Unauthorized, User.NotFound):
                user = None
            self._user = user
        return self._user

    user = property(_get_user)
