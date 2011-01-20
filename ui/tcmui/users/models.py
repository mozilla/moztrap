"""
User-related remote objects.

"""
import logging
from posixpath import join
import urllib

from ..core.api import RemoteObject, ListObject, fields, userAgent
from ..core.models import Company
from ..static.fields import StaticData



log = logging.getLogger('tcmui.users.models')



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


    def activate(self, http=None):
        if getattr(self, '_location', None) is None:
            raise ValueError('Cannot activate %r with no URL to PUT' % self)

        url = join(self._location, "activate/")

        body = urllib.urlencode(
            {"resourceVersionId": self.identity["@version"]}
        )

        headers = {'content-type': 'application/x-www-form-urlencoded'}

        request = self.get_request(
            url=url,
            method='PUT',
            body=body,
            headers=headers
        )

        if http is None:
            http = userAgent
        response, content = http.request(**request)

        log.debug('Activated object, updating from %r', content)

        self.update_from_response(None, response, content)



class UserList(ListObject):
    entryclass = User
    api_name = "users"
    default_url = "users"

    entries = fields.List(fields.Object(User))


    def __unicode__(self):
        return u"%s Users" % len(self)
