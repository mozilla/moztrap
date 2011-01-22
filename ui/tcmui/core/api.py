"""
Core objects for accessing platform API data.

"""
import base64
import cgi
from copy import deepcopy
import logging
from posixpath import join
import urllib
import urlparse

from django.utils.encoding import StrAndUnicode
import remoteobjects
from remoteobjects.http import userAgent

from . import conf
from . import fields
from .. import __version__



log = logging.getLogger('tcmui.core.api')



def add_to_querystring(url, **kwargs):
    """
    Add keys/values in ``kwargs`` to the querystring of ``url``.

    Based on code from remoteobjects' PromiseObject.filter method.

    """
    parts = list(urlparse.urlparse(url))
    queryargs = urlparse.parse_qs(parts[4], keep_blank_values=True)
    queryargs = dict([(k, v[0]) for k, v in queryargs.iteritems()])
    queryargs.update(kwargs)
    parts[4] = urllib.urlencode(queryargs)
    return urlparse.urlunparse(parts)



class ObjectMixin(StrAndUnicode):
    api_base_url = conf.TCM_API_BASE


    def __init__(self, **kwargs):
        """
        Rather than updating __dict__ directly with **kwargs, go through the
        field descriptors for setting initial data.

        """
        super(ObjectMixin, self).__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_request(self, *args, **kwargs):
        """
        Add authorization and user-agent headers, request a JSON-formatted
        response, and prepend TCM_API_BASE to relative URL paths.

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
        request["headers"]["authorization"] = (
            "Basic %s"
            % base64.encodestring(
                "%s:%s" % (user, password)
                )[:-1]
            )

        # Add User-Agent header.
        request["headers"]["user-agent"] = "TCMui/%s" % __version__

        return request


    def update_from_response(self, url, response, content):
        if isinstance(content, str):
            try:
                charset = cgi.parse_header(
                    response["content-type"])[1]["charset"]
            except KeyError:
                charset = "utf-8"
            content = content.decode(charset)
        return super(ObjectMixin, self).update_from_response(
            url, response, content)


    def post(self, obj, http=None):
        """Add another `RemoteObject` to this remote resource through an HTTP
        ``POST`` request.

        Parameter `obj` is a `RemoteObject` instance to save to this
        instance's resource. For example, this (`self`) may be a collection to
        which you want to post an asset (`obj`).

        Optional parameter `http` is the user agent object to use for posting.
        `http` should be compatible with `httplib2.Http` objects.

        """
        if getattr(self, '_location', None) is None:
            raise ValueError('Cannot add %r to %r with no URL to POST to'
                % (obj, self))

        body = urllib.urlencode(obj.to_dict())

        headers = {'content-type': 'application/x-www-form-urlencoded'}

        request = obj.get_request(
            url=self._location,
            method='POST',
            body=body,
            headers=headers
        )

        if http is None:
            http = userAgent
        response, content = http.request(**request)

        log.debug('POSTed new obj, now updating from %r', content)
        # The returned data will include resourceIdentity with url, we don't
        # want to override that with a list URL that isn't even right for the
        # individual object, so we pass in None for the URL.
        obj.update_from_response(None, response, content)


    def _put(self, relative_url=None, full_payload=False, http=None):
        if getattr(self, '_location', None) is None:
            raise ValueError('Cannot PUT %r with no URL' % self)

        if relative_url is not None:
            url = join(self._location, relative_url)
        else:
            url = self._location

        if full_payload:
            body = urllib.urlencode(self.to_dict())
        else:
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

        log.debug('Sending request %r', request)

        if http is None:
            http = userAgent
        response, content = http.request(**request)

        log.debug('Got response %r, updating', response)

        self.update_from_response(None, response, content)


    def put(self, http=None):
        """Save a previously requested `RemoteObject` back to its remote
        resource through an HTTP ``PUT`` request.

        Optional `http` parameter is the user agent object to use. `http`
        objects should be compatible with `httplib2.Http` objects.

        """
        self._put(full_payload=True, http=http)


    def delete(self, http=None):
        """Delete the remote resource represented by the `RemoteObject`
        instance through an HTTP ``DELETE`` request.

        Optional parameter `http` is the user agent object to use. `http`
        objects should be compatible with `httplib2.Http` objects.

        """
        if getattr(self, '_location', None) is None:
            raise ValueError('Cannot delete %r with no URL to DELETE' % self)

        body = urllib.urlencode(
            {"resourceVersionId": self.identity["@version"]}
        )

        headers = {}#@@@{'content-type': 'application/x-www-form-urlencoded'}

        request = self.get_request(method='DELETE', body=body, headers=headers)
        if http is None:
            http = userAgent
        response, content = http.request(**request)

        self.raise_for_response(self._location, response, content)

        log.debug('Deleted the remote resource, now disconnecting %r', self)

        # No more resource.
        self._location = None
        self.identity = None


    def to_dict(self):
        """Encodes the DataObject to a dictionary."""
        data = {}
        for field_name, field in self.fields.iteritems():
            data.update(field.submit_data(self))
        return data


    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)



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
        try:
            if self._delivered and "@url" in self.identity:
                return self.identity["@url"]
        except TypeError:
            pass
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
