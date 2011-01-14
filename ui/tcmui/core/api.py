"""
Core objects for accessing platform API data.

"""
import base64
import cgi
import urllib
import urlparse

from remoteobjects import RemoteObject, ListObject, fields

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



class TCMMixin(object):
    def get_request(self, *args, **kwargs):
        """
        Add authorization header and request a JSON-formatted response.

        """
        user = kwargs.pop("user", conf.TCM_ADMIN_USER)
        password = kwargs.pop("password", conf.TCM_ADMIN_PASS)

        request = super(TCMMixin, self).get_request(*args, **kwargs)
        request["uri"] = add_to_querystring(request["uri"], _type="json")

        request["headers"]["Authorization"] = (
            "Basic %s"
            % base64.encodestring(
                "%s:%s" % (user, password)
                )[:-1]
            )

        return request



class TCMRemoteObject(TCMMixin, RemoteObject):
    @property
    def api_name(self):
        return self.__class__.__name__.lower()


    def update_from_dict(self, data):
        """
        Clean up the JSON data.

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

        We pass on just the inner-most dictionary, with "ns1." prefixes
        stripped from keys.

        In order to also support data passed in from TCMListObject instances,
        both the outer dictionary wrapper and the list wrapper inside that are
        optional, and will be stripped only if found.

        """
        new = {}
        wrapper_key = "ns1.%s" % self.api_name
        if wrapper_key in data:
            data = data[wrapper_key]
        if isinstance(data, list):
            data = data[0]
        for key, val in data.iteritems():
            if val == {"@xsi.nil": "true"}:
                val = None
            if key.startswith("ns1."):
                key = key[len("ns1."):]

            new[key] = val

        return super(TCMRemoteObject, self).update_from_dict(new)



class TCMListObject(TCMMixin, ListObject):
    def update_from_dict(self, data):
        """
        Clean up the JSON data.

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

        We pass on a list of data dictionaries. We don't do any cleaning within
        those dictionaries (e.g. stripping "ns1" prefix, etc.), as the
        individual TCMRemoteObject will take care of that.

        """
        data = data["ns1.searchResult"][0]
        num_results = data["ns1.totalResults"]
        data = data["ns1.%s" % self.api_name]
        data = data["ns1.%s" % self.entryclass().api_name]
        # @@@ API (oddly) eliminates list wrapper for length-1 lists.
        if num_results == 1:
            data = [data]
        return super(TCMListObject, self).update_from_dict(data)
