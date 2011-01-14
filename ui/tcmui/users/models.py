"""
User-related remote objects.

"""
from ..core.api import TCMRemoteObject, TCMListObject, fields



class User(TCMRemoteObject):
    # @@@
    # identity = ResourceIdentityField()
    email = fields.Field()
    firstName = fields.Field()
    lastName = fields.Field()
    password = fields.Field()
    screenName = fields.Field()
    # @@@
    # userStatus = StaticDataField("USERSTATUS")


class UserList(TCMListObject):
    entryclass = User
    api_name = "users"

    entries = fields.List(fields.Object(User))
