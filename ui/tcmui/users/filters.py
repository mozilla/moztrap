from ..core.filters import LocatorFieldFilter

from .models import UserList



class UserFieldFilter(LocatorFieldFilter):
    target = UserList
