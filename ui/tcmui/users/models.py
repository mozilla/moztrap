"""
User-related remote objects.

"""
from ..core.api import TCMRemoteObject, fields



class User(TCMRemoteObject):
    email = fields.Field()
    firstName = fields.Field()
    lastName = fields.Field()
    password = fields.Field()
    screenName = fields.Field()
