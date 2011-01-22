"""
User-related remote objects.

"""
import urllib

from ..core.api import RemoteObject, ListObject, fields
from ..core.models import Company
from ..static.fields import StaticData



class User(RemoteObject):
    company = fields.Locator(Company)
    email = fields.Field()
    firstName = fields.Field()
    lastName = fields.Field()
    password = fields.Field()
    screenName = fields.Field()
    userStatus = StaticData("USERSTATUS")


    def __unicode__(self):
        return self.screenName


    def activate(self):
        self._put(relative_url="activate")


    def deactivate(self):
        self._put(relative_url="deactivate")


    def emailchange(self, newemail):
        self._put(relative_url="emailchange/%s" % urllib.quote(newemail))


    def emailconfirm(self):
        self._put(relative_url="emailconfirm")


    def passwordchange(self, newpassword):
        self._put(relative_url="passwordchange/%s" % urllib.quote(newpassword))



class UserList(ListObject):
    entryclass = User
    api_name = "users"
    default_url = "users"

    entries = fields.List(fields.Object(User))


    def __unicode__(self):
        return u"%s Users" % len(self)


    def login(self):
        self._put(
            relative_url="login",
            version_payload=False,
            update_from_response=False,
            )
