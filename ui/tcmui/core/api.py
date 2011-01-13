"""
Core objects for accessing platform API data.

"""
import base64
import cgi
import urllib
import urlparse

from remoteobjects import RemoteObject, fields

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



class TCMRemoteObject(RemoteObject):
    def get_request(self, *args, **kwargs):
        """
        Add authorization header and request a JSON-formatted response.

        """
        user = kwargs.pop("user", conf.TCM_ADMIN_USER)
        password = kwargs.pop("password", conf.TCM_ADMIN_PASS)

        request = super(TCMRemoteObject, self).get_request(*args, **kwargs)
        request["uri"] = add_to_querystring(request["uri"], _type="json")

        request["headers"]["Authorization"] = (
            "Basic %s"
            % base64.encodestring(
                "%s:%s" % (user, password)
                )[:-1]
            )

        return request


    @property
    def api_name(self):
        return self.__class__.__name__.lower()


    def update_from_dict(self, data):
        """
        Clean up the JSON data.

        """
        new = {}
        for key, val in data["ns1.%s" % self.api_name][0].iteritems():
            if val == {"@xsi.nil": "true"}:
                val = None
            if key.startswith("ns1."):
                key = key[len("ns1."):]

            new[key] = val

        return super(TCMRemoteObject, self).update_from_dict(new)
