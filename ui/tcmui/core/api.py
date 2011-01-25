"""
Core objects for accessing platform API data.

"""
import base64
import cgi
from copy import deepcopy
import logging
from posixpath import join
import simplejson as json
import urllib
import urlparse

from django.utils.encoding import StrAndUnicode
import remoteobjects
from remoteobjects.http import userAgent

from . import conf
from . import fields
from .. import __version__



log = logging.getLogger('tcmui.core.api')



class Credentials(object):
    def __init__(self, user, password):
        self.user, self.password = user, password


    def __repr__(self):
        return "<Credentials: %s>" % self.user



admin = Credentials(conf.TCM_ADMIN_USER, conf.TCM_ADMIN_PASS)



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
        self.auth = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_request(self, *args, **kwargs):
        """
        Add authorization and user-agent headers, request a JSON-formatted
        response, and prepend TCM_API_BASE to relative URL paths.

        """
        auth = kwargs.pop("auth", self.auth)

        request = super(ObjectMixin, self).get_request(*args, **kwargs)

        # Add API base URL to relative paths.
        if "://" not in request["uri"]:
            request["uri"] = urlparse.urljoin(self.api_base_url, request["uri"])

        # Request a JSON response.
        request["uri"] = add_to_querystring(request["uri"], _type="json")

        # Add Authorization header.
        if auth is not None:
            request["headers"]["authorization"] = (
                "Basic %s"
                % base64.encodestring(
                    "%s:%s" % (auth.user, auth.password)
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


    @classmethod
    def get(cls, url, **kwargs):
        obj = super(ObjectMixin, cls).get(url, **kwargs)
        obj.auth = kwargs.get("auth")
        return obj


    def post(self, obj, **kwargs):
        """Add another `RemoteObject` to this remote resource through an HTTP
        ``POST`` request.

        Parameter `obj` is a `RemoteObject` instance to save to this
        instance's resource. For example, this (`self`) may be a collection to
        which you want to post an asset (`obj`).

        """
        if getattr(self, "_location", None) is None:
            raise ValueError("Cannot add %r to %r with no URL to POST to"
                % (obj, self))

        body = urllib.urlencode(obj.to_dict())

        headers = {"content-type": "application/x-www-form-urlencoded"}

        if "auth" not in kwargs and self.auth is not None:
            kwargs["auth"] = self.auth

        request = obj.get_request(
            url=self._location,
            method="POST",
            body=body,
            headers=headers,
            **kwargs
        )

        response, content = userAgent.request(**request)

        log.debug("POSTed new obj, now updating from %r", content)
        # The returned data will include resourceIdentity with url, we don't
        # want to override that with a list URL that isn't even right for the
        # individual object, so we pass in None for the URL.
        obj.update_from_response(None, response, content)


    def _put(self, relative_url=None, full_payload=False, version_payload=True,
             update_from_response=True, extra_payload=None,
             default_content_type="application/x-www-form-urlencoded",
             **kw):
        if getattr(self, "_location", None) is None:
            raise ValueError("Cannot PUT %r with no URL" % self)

        kw["method"] = "PUT"

        if "url" not in kw:
            if relative_url is not None:
                kw["url"] = join(self._location, relative_url)
            else:
                kw["url"] = self._location

        if full_payload:
            payload = self.to_dict()
        elif version_payload:
            payload = {"resourceVersionId": self.identity["@version"]}
        else:
            payload = {}

        if extra_payload:
            payload.update(extra_payload)

        headers = kw.setdefault("headers", {})
        headers.setdefault("content-type", default_content_type)

        if payload:
            if headers["content-type"] == "application/json":
                kw["body"] = json.dumps(payload)
            else:
                kw["body"] = urllib.urlencode(payload, doseq=True)

        request = self.get_request(**kw)

        log.debug("Sending request %r", request)

        response, content = userAgent.request(**request)

        if update_from_response:
            log.debug("Got response %r, updating", response)

            self.update_from_response(None, response, content)
        else:
            log.debug("Got response %r, raising", response)
            self.raise_for_response(self._location, response, content)


    def put(self, **kwargs):
        """Save a previously requested `RemoteObject` back to its remote
        resource through an HTTP ``PUT`` request.

        Optional `http` parameter is the user agent object to use. `http`
        objects should be compatible with `httplib2.Http` objects.

        """
        self._put(full_payload=True, **kwargs)


    def delete(self, **kwargs):
        """Delete the remote resource represented by the `RemoteObject`
        instance through an HTTP ``DELETE`` request.

        Optional parameter `http` is the user agent object to use. `http`
        objects should be compatible with `httplib2.Http` objects.

        """
        if getattr(self, "_location", None) is None:
            raise ValueError("Cannot delete %r with no URL to DELETE" % self)

        body = urllib.urlencode(
            {"resourceVersionId": self.identity["@version"]}
        )

        headers = {"content-type": "application/x-www-form-urlencoded"}

        request = self.get_request(
            method="DELETE",
            body=body,
            headers=headers,
            **kwargs
        )

        response, content = userAgent.request(**request)

        self.raise_for_response(self._location, response, content)

        log.debug("Deleted the remote resource, now disconnecting %r", self)

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
        outer_key = None
        for candidate_key in [
            "ns1.ArrayOf%s" % self.entryclass.__name__,
            "ns1.searchResult"
            ]:
            if candidate_key in data:
                outer_key = candidate_key
                break
        if outer_key is not None:
            data = data[outer_key][0]
            if outer_key == "ns1.searchResult":
                data = data["ns1.%s" % self.api_name]
            try:
                data = data["ns1.%s" % self.entryclass().api_name]
            except KeyError:
                data = []
            # Because this JSON is BadgerFish-translated XML
            # (http://ajaxian.com/archives/badgerfish-translating-xml-to-json)
            # length-1 lists are not sent as lists, so we re-listify.
            if not isinstance(data, list):
                data = [data]
        return super(ListObject, self).update_from_dict(data)


    @classmethod
    def get(cls, url=None, auth=None):
        if url is None:
            try:
                url = cls.default_url
            except AttributeError:
                raise ValueError("%s has no default URL; .get() requires url."
                                 % cls)
        obj = super(ListObject, cls).get(url)
        obj.auth = auth
        return obj


    def __getitem__(self, *args, **kwargs):
        obj = super(ListObject, self).__getitem__(*args, **kwargs)
        obj.auth = self.auth
        return obj


    def __iter__(self, *args, **kwargs):
        for obj in super(ListObject, self).__iter__(*args, **kwargs):
            obj.auth = self.auth
            yield obj
