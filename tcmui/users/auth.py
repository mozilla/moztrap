from ..core.auth import Credentials
from .models import User



class UserCredentials(Credentials):
    """
    Expands the core Credentials object with lazy ``user`` and
    ``permission_codes`` properties.

    """
    def __init__(self, *args, **kwargs):
        super(UserCredentials, self).__init__(*args, **kwargs)
        self._user = None
        self._permission_codes = None


    @property
    def user(self):
        if self._user is None:
            try:
                user = User.current(auth=self, cache=False)
                user.deliver()
            except (User.Forbidden, User.Unauthorized, User.NotFound):
                user = None
            self._user = user
        return self._user


    @property
    def permission_codes(self):
        if self._permission_codes is None:
            self._permission_codes = self.user.permissionCodes
        return self._permission_codes
