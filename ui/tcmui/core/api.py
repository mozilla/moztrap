"""
Core objects for accessing platform API data.

"""
import base64
import cgi
import urllib
import urlparse

import remoteobjects

from . import conf
from . import fields



def add_to_querystring(url, **kwargs):
    """
    Add keys/values in ``kwargs`` to the querystring of ``url``.

    Based on code from remoteobjects' PromiseObject.filter method.

    """
    parts = list(urlparse.urlparse(url))
    queryargs = cgi.parse_qs(parts[4], keep_blank_values=True)
    queryargs = dict([(k, v[0]) for k, v in queryargs.iteritems()])
    queryargs.update(kwargs)
    parts[4] = urllib.urlencode(queryargs)
    return urlparse.urlunparse(parts)



class ObjectMixin(object):
    api_base_url = conf.TCM_API_BASE
    
    def get_request(self, *args, **kwargs):
        """
        Add authorization header, request a JSON-formatted response, and
        prepend TCM_API_BASE to relative URL paths.

        """
        user = kwargs.pop("user", conf.TCM_ADMIN_USER)
        password = kwargs.pop("password", conf.TCM_ADMIN_PASS)

        request = super(ObjectMixin, self).get_request(*args, **kwargs)

        # Add API base URL to relative paths.
        if "://" not in request["uri"]:
            request["uri"] = urlparse.urljoin(self.api_base_url, request["uri"])

        # Request a JSON response.
        request["uri"] = add_to_querystring(request["uri"], _type="json")

        # Add Authorization header.
        request["headers"]["Authorization"] = (
            "Basic %s"
            % base64.encodestring(
                "%s:%s" % (user, password)
                )[:-1]
            )

        return request



class RemoteObject(ObjectMixin, remoteobjects.RemoteObject):
    identity = fields.ResourceIdentity()


    @property
    def api_name(self):
        return self.__class__.__name__.lower()


    def _set_location(self, val):
        self._location_override = val


    def _get_location(self):
        if self._location_override:
            return self._location_override
        # Avoid infinite loopage; take care to not trigger delivery
        if "identity" in self.__dict__ and "@url" in self.identity:
            return self.identity["@url"]
        return None


    _location = property(_get_location, _set_location)


    def update_from_dict(self, data):
        """
        Unwrap the JSON data.

        We expect to get data in a form like this:

        {
           "ns1.user":[
              {
                 "ns1.screenName":"userName1",
                 "ns1.userStatusId":1
                 ... more user data ...
              }
           ]
        }

        We pass on just the inner-most dictionary.

        In order to also support data passed in from ListObject instances,
        the unwrapping is optional; if we get just a straight data dictionary,
        we'll pass that on untouched.

        """
        wrapper_key = "ns1.%s" % self.api_name
        if wrapper_key in data:
            data = data[wrapper_key][0]
        return super(RemoteObject, self).update_from_dict(data)



class ListObject(ObjectMixin, remoteobjects.ListObject):
    def update_from_dict(self, data):
        """
        Unwrap the JSON data.

        We expect to get data in a form like this:

        {
           "ns1.searchResult":[
              {
                 "@xsi.type":"ns1:searchResult",
                 "ns1.companies":{
                    "ns1.company":[
                       {
                          "@xsi.type":"ns1:company",
                          ... company data ...
                       },
                       {
                          "@xsi.type":"ns1:company",
                          ... company data ...
                       }
                    ]
                 },
                 "ns1.totalResults":2
              }
           ]
        }

        We pass on the inner list of data dictionaries.

        """
        if "ns1.searchResult" in data:
            data = data["ns1.searchResult"][0]
            num_results = data["ns1.totalResults"]
            data = data["ns1.%s" % self.api_name]
            data = data["ns1.%s" % self.entryclass().api_name]
            # Because this JSON is BadgerFish-translated XML
            # (http://ajaxian.com/archives/badgerfish-translating-xml-to-json)
            # length-1 lists are not sent as lists, so we re-listify.
            if num_results == 1:
                data = [data]
        return super(ListObject, self).update_from_dict(data)


    @classmethod
    def get(cls, url=None, http=None, **kwargs):
        if url is None:
            try:
                url = cls.default_url
            except AttributeError:
                raise ValueError("%s has no default URL; .get() requires url."
                                 % cls)
        return super(ObjectMixin, cls).get(url, http, **kwargs)
