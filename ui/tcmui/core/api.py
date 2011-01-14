"""
Core objects for accessing platform API data.

"""
import base64
import cgi
import urllib
import urlparse

import remoteobjects

from . import conf



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
    def get_request(self, *args, **kwargs):
        """
        Add authorization header and request a JSON-formatted response.

        """
        user = kwargs.pop("user", conf.TCM_ADMIN_USER)
        password = kwargs.pop("password", conf.TCM_ADMIN_PASS)

        request = super(ObjectMixin, self).get_request(*args, **kwargs)
        request["uri"] = add_to_querystring(request["uri"], _type="json")

        request["headers"]["Authorization"] = (
            "Basic %s"
            % base64.encodestring(
                "%s:%s" % (user, password)
                )[:-1]
            )

        return request



class RemoteObject(ObjectMixin, remoteobjects.RemoteObject):
    @property
    def api_name(self):
        return self.__class__.__name__.lower()


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



class FieldMixin(object):
    def install(self, attrname, cls):
        super(FieldMixin, self).install(attrname, cls)

        self.api_name = "ns1.%s" % self.api_name


    def decode(self, value):
        if value == {"@xsi.nil": "true"}:
            value = None
        return super(FieldMixin, self).decode(value)



class Field(FieldMixin, remoteobjects.fields.Field):
    pass



class Locator(Field):
    def __init__(self, cls, api_name=None, default=None):
        self.cls = cls
        super(Locator, self).__init__(api_name, default)


    def install(self, attrname, cls):
        super(Locator, self).install(attrname, cls)

        self.api_name = "%sLocator" % self.api_name


    def __get__(self, obj, cls):
        if obj is None:
            return self

        data = super(Locator, self).__get__(obj, cls)

        if data and "@url" in data:
            return self.cls.get(data["@url"])
        return data


List = remoteobjects.fields.List
Object = remoteobjects.fields.Object
