"""
User-related remote objects.

"""
from ..core import api
from ..core.models import Company


class User(api.RemoteObject):
    # @@@ identity = api.ResourceIdentity()
    company = api.Locator(Company)
    email = api.Field()
    firstName = api.Field()
    lastName = api.Field()
    password = api.Field()
    screenName = api.Field()
    # @@@
    # userStatus = api.StaticDataField("USERSTATUS")


class UserList(api.ListObject):
    entryclass = User
    api_name = "users"

    entries = api.List(api.Object(User))
