"""
User-related remote objects.

"""
from ..core import api



class User(api.RemoteObject):
    # @@@ identity = ResourceIdentityField()
    # @@@ company = Link('Company')
    email = api.Field()
    firstName = api.Field()
    lastName = api.Field()
    password = api.Field()
    screenName = api.Field()
    # @@@
    # userStatus = StaticDataField("USERSTATUS")


class UserList(api.ListObject):
    entryclass = User
    api_name = "users"

    entries = api.List(api.Object(User))
