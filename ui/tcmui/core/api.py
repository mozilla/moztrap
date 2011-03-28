"""
Core objects for accessing platform API data.

"""
import cgi
import httplib
import httplib2
import logging
from posixpath import join
import simplejson as json
import urllib

from django.core.cache import cache
from django.utils.encoding import StrAndUnicode
import remoteobjects
from remoteobjects.http import userAgent

from .conf import conf
from . import fields
from . import sort, pagination
from . import util
from .. import __version__



log = logging.getLogger('tcmui.core.api')



class CachedHttp(httplib2.Http):
    def request(self, **kwargs):
        method = kwargs.get("method", "GET").upper()
        if method == "GET":
            cache_key = kwargs["uri"]
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        response, content = super(CachedHttp, self).request(**kwargs)

        # only cache 200 OK responses
        if method == "GET" and response.status == httplib.OK:
            cache.set(cache_key, (response, content), conf.TCM_CACHE_SECONDS)

        return (response, content)



cachedUserAgent = CachedHttp()



class ObjectMixin(StrAndUnicode):
    api_base_url = conf.TCM_API_BASE
    cache = False
    _filterable_fields = None


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
        auth = kwargs.pop("auth", None)
        if auth is None:
            auth = self.auth

        request = super(ObjectMixin, self).get_request(*args, **kwargs)

        # Add API base URL to relative paths.
        if "://" not in request["uri"]:
            request["uri"] = join(self.api_base_url, request["uri"])

        # Request a JSON response.
        request["uri"] = util.add_to_querystring(request["uri"], _type="json")

        # Add authorization headers.
        if auth is not None:
            request["headers"].update(auth.headers())

        # Add User-Agent header.
        request["headers"]["user-agent"] = "TCMui/%s" % __version__

        return request


    class Conflict(httplib.HTTPException):
        """An HTTPException thrown when the server reports that the requested
        action cannot be taken because it conflicts with the current state of
        the resource.

        This could be due to trying to update an out-of-date version of a
        resource, or because a resource can't be deleted because it is
        referenced by other resources, or because supplied data for a new
        resource violates unique constraints on that type of resource, or for
        other reasons. It's up to the catching code to determine the meaning of
        this exception, based on context and the error string from the server
        (which will be available as the ``response_error`` attribute).

        This exception corresponds to the HTTP status code 409.

        """
        pass


    @classmethod
    def exception_classes(cls):
        """
        Maps httplib exceptional status codes to Python exception classes.

        """
        return {
            httplib.CONFLICT: cls.Conflict,
            httplib.NOT_FOUND: cls.NotFound,
            httplib.UNAUTHORIZED: cls.Unauthorized,
            httplib.PRECONDITION_FAILED: cls.PreconditionFailed,
            httplib.FORBIDDEN: cls.Forbidden,
            httplib.BAD_REQUEST: cls.RequestError,
            httplib.INTERNAL_SERVER_ERROR: cls.ServerError,
            }


    @classmethod
    def raise_for_response(cls, url, response, content):
        """
        Raises exceptions corresponding to invalid HTTP responses that
        instances of this class can't be updated from.

        """
        # Turn exceptional httplib2 responses into exceptions.
        classname = cls.__name__
        exception_classes = cls.exception_classes()
        if response.status in exception_classes:
            exc_cls = exception_classes[response.status]

            # try to pull out an error
            content_type = cgi.parse_header(response.get("content-type", ""))[0]
            if content_type == "application/json":
                data = json.loads(content)
                # error format is e.g. {"errors":[{"error":"email.in.use"}]}
                # currently only one error is returned at a time
                error = data.get("errors", [{}])[0].get("error", "")
            else:
                error = str(content)

            exc = exc_cls(
                '%d %s requesting %s %s: %s'
                % (response.status, response.reason, classname, url, error)
                )
            exc.response_error = error
            raise exc

        try:
            response_has_content = cls.response_has_content[response.status]
        except KeyError:
            # we only expect the statuses that we know do or don't have content
            raise cls.BadResponse('Unexpected response requesting %s %s: %d %s'
                % (classname, url, response.status, response.reason))

        try:
            location_header = cls.location_headers[response.status]
        except KeyError:
            pass
        else:
            if cls.location_header_required.get(response.status) and location_header.lower() not in response:
                raise cls.BadResponse(
                    "%r header missing from %d %s response requesting %s %s"
                    % (location_header, response.status, response.reason,
                       classname, url))

        if not response_has_content:
            # then there's no content-type either, so we're done
            return

        # check that the response body was json
        content_type = response.get('content-type', '').split(';', 1)[0].strip()
        if content_type not in cls.content_types:
            raise cls.BadResponse(
                'Bad response fetching %s %s: content-type %s is not an expected type'
                % (classname, url, response.get('content-type')))


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
        if cls.cache and "http" not in kwargs:
            kwargs["http"] = cachedUserAgent
        obj = super(ObjectMixin, cls).get(url, **kwargs)
        obj.auth = kwargs.get("auth")
        return obj


    def _put(self, **kwargs):
        return self._request("PUT", **kwargs)


    def _post(self, **kwargs):
        return self._request("POST", **kwargs)


    def _delete(self, **kwargs):
        return self._request("DELETE", **kwargs)


    def _request(self, method, relative_url=None, full_payload=False,
                 version_payload=True, update_from_response=False,
                 extra_payload=None,
                 # @@@ change default to application/json once API supports it
                 default_content_type="application/x-www-form-urlencoded",
                 **kw):
        """
        Swiss army knife utility method to make HTTP requests relative to this
        object.

        ``method``
            HTTP method to use.

        ``relative_url``
            URL relative to this object's location; if None, this object's
            location is used.

        ``full_payload``
            If True, send the full contents of this object's to_dict() as the
            payload. If set to another object, send the contents of that
            object's to_dict() instead.

        ``version_payload``
            If True, send this object's resource version as originalVersionId
            in payload. If set to another object, use that object's resource
            version instead. Has no effect if full_payload is specified.

        ``extra_payload``
            A dictionary of extra payload data to send.

        ``update_from_response``
            If True, update this object from the response. If set to another
            object, update that object instead.

        ``default_content_type``
            Send the body payload as this content type. Supported content types
            are "application/json" and "application/x-www-form-urlencoded".

        All other keyword arguments are passed along directly to get_request
        (possibly modified as dictated by the other arguments).

        Returns the httplib2 Response object, in case calling method needs to
        pull other data out of the response (such as cookies).

        """
        kw["method"] = method

        if "url" not in kw:
            if getattr(self, "_location", None) is None:
                raise ValueError("Cannot %s %r with no URL" % (method, self))
            if relative_url is not None:
                kw["url"] = join(self._location, relative_url)
            else:
                kw["url"] = self._location

        payload = {}
        if full_payload:
            if full_payload is True:
                full_payload = self
            payload.update(full_payload.to_dict())
        elif version_payload:
            if version_payload is True:
                version_payload = self
            if "identity" in version_payload.fields:
                field = version_payload.fields["identity"]
                payload.update(field.submit_data(version_payload))
        if extra_payload:
            payload.update(extra_payload)

        headers = kw.setdefault("headers", {})
        headers.setdefault("content-type", default_content_type)

        if payload:
            if headers["content-type"] == "application/json":
                kw["body"] = json.dumps(payload)
            elif headers["content-type"] == "application/x-www-form-urlencoded":
                kw["body"] = urllib.urlencode(payload, doseq=True)
            else:
                raise ValueError("content type '%s' is not supported"
                                 % headers["content-type"])

        request = self.get_request(**kw)

        log.debug("Sending request %r", request)

        response, content = userAgent.request(**request)

        if update_from_response:
            log.debug("Got response %r, updating", response)

            if not hasattr(update_from_response, "update_from_response"):
                update_from_response = self

            update_from_response.update_from_response(None, response, content)
        else:
            log.debug("Got response %r, raising", response)
            self.raise_for_response(self._location, response, content)

        return response


    def post(self, obj, **kwargs):
        """Add another `RemoteObject` to this remote resource through an HTTP
        ``POST`` request.

        Parameter `obj` is a `RemoteObject` instance to save to this
        instance's resource. For example, this (`self`) may be a collection to
        which you want to post an asset (`obj`).

        """
        self._request(
            "POST",
            full_payload=obj,
            update_from_response=obj,
            **kwargs)
        if obj.auth is None:
            obj.auth = kwargs.get("auth", self.auth)


    def put(self, **kwargs):
        """Save a previously requested `RemoteObject` back to its remote
        resource through an HTTP ``PUT`` request.

        Optional `http` parameter is the user agent object to use. `http`
        objects should be compatible with `httplib2.Http` objects.

        """
        self._put(full_payload=True, update_from_response=True, **kwargs)


    def delete(self, **kwargs):
        """Delete the remote resource represented by the `RemoteObject`
        instance through an HTTP ``DELETE`` request.

        Optional parameter `http` is the user agent object to use. `http`
        objects should be compatible with `httplib2.Http` objects.

        """
        self._delete(**kwargs)

        # No more resource.
        self._location = None
        self.identity = None


    def to_dict(self):
        """Encodes the DataObject to a dictionary."""
        data = {}
        for field_name, field in self.fields.iteritems():
            data.update(field.submit_data(self))
        return data


    @classmethod
    def filterable_fields(cls):
        if cls._filterable_fields is None:
            cls._filterable_fields = dict(
                (n, f) for (n, f) in cls.fields.iteritems()
                if getattr(f, "api_filter_name", False))
        return cls._filterable_fields


    def filter(self, **kwargs):
        """
        Returns a new instance with filter parameters added as parameters to
        the instance's query string.

        Resolves Python field names to correct API names, and ignores any
        requested filters that don't map to an actual field.

        """
        auth = kwargs.pop("auth", self.auth)

        valid_fieldnames = set(self.filterable_fields().keys())
        filters = {}
        for (k, v) in kwargs.iteritems():
            if k == "sortfield" and v in valid_fieldnames:
                filters[k] = self.filterable_fields()[v].api_filter_name
            elif k == "sortdirection" and v in sort.DIRECTIONS:
                filters[k] = v
            elif k == "pagesize":
                filters[k] = pagination.positive_integer(
                    v, pagination.DEFAULT_PAGESIZE)
            elif k == "pagenumber":
                filters[k] = pagination.positive_integer(
                    v, 1)
            elif k in valid_fieldnames:
                filters[self.filterable_fields()[k].api_filter_name] = v

        newurl = util.add_to_querystring(self._location, **filters)

        return self.get(newurl, auth=auth)


    def refresh(self):
        return self.__class__.get(self._location, auth=self.auth)


    def __repr__(self):
        if self._delivered:
            return "<%s: %s>" % (self.__class__.__name__, self)
        else:
            return "<%s: %s>" % (self.__class__.__name__, self._location)



class RemoteObject(ObjectMixin, remoteobjects.RemoteObject):
    identity = fields.ResourceIdentity()
    timeline = fields.TimelineField()


    @property
    def api_name(self):
        return self.__class__.__name__.lower()


    def _set_location(self, val):
        self._location_fallback = val


    def _get_location(self):
        # Avoid infinite loopage; take care to not trigger delivery
        try:
            if self._delivered and "@url" in self.identity:
                return self.identity["@url"]
        except TypeError:
            pass
        if self._location_fallback:
            return self._location_fallback
        return None


    _location = property(_get_location, _set_location)


    @property
    def id(self):
        return util.id_for_object(self)


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
        if wrapper_key in data and isinstance(data[wrapper_key], list):
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

        In some cases (when we're drilling down to linked resources rather than
        doing a top-level search) the outer two layers are replaced by a
        dictionary with a single "ArrayOfX" key; we support that as well.

        """
        outer_key = None
        for candidate_key in [
            "ns1.ArrayOf%s" % self.array_name.title(),
            "ns1.searchResult"
            ]:
            if candidate_key in data:
                outer_key = candidate_key
                break
        if outer_key is not None:
            data = data[outer_key][0]
            if outer_key == "ns1.searchResult":
                self._totalResults = int(data["ns1.totalResults"])
                data = data["ns1.%s" % self.api_name]
            try:
                data = data["ns1.%s" % self.entryclass().api_name]
            except (KeyError, TypeError):
                data = []
            # Because this JSON is BadgerFish-translated XML
            # (http://ajaxian.com/archives/badgerfish-translating-xml-to-json)
            # length-1 lists are not sent as lists, so we re-listify.
            if not isinstance(data, list):
                data = [data]
        return super(ListObject, self).update_from_dict(data)


    @property
    def totalResults(self):
        if not self._delivered:
            self.deliver()
        return self._totalResults


    @classmethod
    def get(cls, url=None, **kwargs):
        if url is None:
            try:
                url = cls.default_url
            except AttributeError:
                raise ValueError("%s has no default URL; .get() requires url."
                                 % cls)
        obj = super(ListObject, cls).get(url, **kwargs)
        obj.auth = kwargs.get("auth", None)
        return obj


    @classmethod
    def ours(cls, **kwargs):
        return cls.get(**kwargs).filter(company=conf.TCM_COMPANY_ID)


    @property
    def submit_ids_name(self):
        classname = self.entryclass.__name__
        return util.lc_first(classname) + "Ids"


    @property
    def array_name(self):
        return self.entryclass.__name__.lower()


    def put(self, **kwargs):
        payload_data = {
            self.submit_ids_name: [util.id_for_object(o) for o in self]}

        self._put(
            extra_payload=payload_data,
            **kwargs)

    def __getitem__(self, *args, **kwargs):
        obj = super(ListObject, self).__getitem__(*args, **kwargs)
        obj.auth = self.auth
        return obj


    def __iter__(self, *args, **kwargs):
        for obj in super(ListObject, self).__iter__(*args, **kwargs):
            if isinstance(obj, RemoteObject):
                obj.auth = self.auth
            yield obj


    @classmethod
    def filterable_fields(cls):
        return cls.entryclass.filterable_fields()


    def sort(self, field, direction=sort.DEFAULT):
        if field is None:
            return self
        return self.filter(sortfield=field, sortdirection=direction)


    def paginate(self, pagesize=None, pagenumber=None):
        if pagesize == None and pagenumber == None:
            return self

        return self.filter(
            pagesize=pagination.positive_integer(
                pagesize, pagination.DEFAULT_PAGESIZE),
            pagenumber=pagination.positive_integer(pagenumber, 1))


    @classmethod
    def get_by_id(cls, id_, **kwargs):
        try:
            return cls.entryclass.get(join(cls.default_url, str(id_)), **kwargs)
        except AttributeError:
            raise ValueError("%s has no default URL; .get_by_id() requires url."
                             % cls)


    def __unicode__(self):
        return u"[%s]" % ", ".join([repr(e) for e in self])



class Activatable(object):
    def activate(self, **kwargs):
        self._put(
            relative_url="activate",
            update_from_response=True,
            **kwargs)


    def deactivate(self, **kwargs):
        self._put(
            relative_url="deactivate",
            update_from_response=True,
            **kwargs)
