from contextlib import contextmanager
from functools import partial
import urlparse

from django.core.cache import get_cache
from django.test.signals import template_rendered
from django.test.client import RequestFactory, store_rendered_templates
from mock import patch
from unittest2 import TestCase

from .builder import ListBuilder
from .core.builders import companies
from .products.builders import products
from .responses import response, make_identity
from .static.builders import codevalues
from .users.builders import users



def fill_cache(cache, values_dict):
    """
    Fill a mock cache object with some keys and values.

    """
    cache.get.side_effect = lambda k, d=None: values_dict.get(k, d)



def setup_responses(http, response_dict):
    """
    Setup a mock http object with some responses to given
    URLs. ``response_dict`` should map full URLs (including query string) to
    the (response, content) tuple that will be returned (equivalent to the
    return value of the httplib2.Http.request method).

    """
    url_dict = dict((Url(k), v) for k, v in response_dict.iteritems())
    def request(*args, **kwargs):
        uri = Url(kwargs["uri"])
        try:
            return url_dict[uri]
        except KeyError:
            return response(
                {"errors": [
                        {"error":
                             "Mock got unexpected request URI: %s \n"
                         " -- Options are %s --" % (uri, response_dict.keys())}
                        ]
                 }
                , 500)

    http.request.side_effect = request


COMMON_RESPONSES = {
    "http://fake.base/rest/companies/1?_type=json":
        response(companies.one(
            resourceIdentity=make_identity(id=1, url="companies/1"))),
    "http://fake.base/rest/users?_type=json":
        response(users.searchresult({})),
    "http://fake.base/rest/products?_type=json":
        response(products.searchresult({})),
    "http://fake.base/staticData/values/TESTCYCLESTATUS?_type=json":
        response(codevalues.array(
            {"description": "DRAFT", "id": 1},
            {"description": "ACTIVE", "id": 2},
            {"description": "LOCKED", "id": 3},
            {"description": "CLOSED", "id": 4},
            {"description": "DISCARDED", "id": 5},
            )),
    "http://fake.base/staticData/values/TESTRUNSTATUS?_type=json":
        response(codevalues.array(
            {"description": "DRAFT", "id": 1},
            {"description": "ACTIVE", "id": 2},
            {"description": "LOCKED", "id": 3},
            {"description": "CLOSED", "id": 4},
            {"description": "DISCARDED", "id": 5},
            )),
    "http://fake.base/staticData/values/TESTCASESTATUS?_type=json":
        response(codevalues.array(
            {"description": "DRAFT", "id": 1},
            {"description": "ACTIVE", "id": 2},
            {"description": "LOCKED", "id": 3},
            {"description": "CLOSED", "id": 4},
            {"description": "DISCARDED", "id": 5},
            )),
    "http://fake.base/staticData/values/TESTRUNRESULTSTATUS?_type=json":
        response(codevalues.array(
            {"description": "PENDING", "id": 1},
            {"description": "PASSED", "id": 2},
            {"description": "FAILED", "id": 3},
            {"description": "BLOCKED", "id": 4},
            {"description": "STARTED", "id": 5},
            {"description": "INVALIDATED", "id": 6},
            )),
    "http://fake.base/staticData/values/APPROVALSTATUS?_type=json":
        response(codevalues.array(
            {"description": "PENDING", "id": 1},
            {"description": "APPROVED", "id": 2},
            {"description": "REJECTED", "id": 3},
            ))
    }


def setup_common_responses(http, response_dict):
    """
    A version of ``setup_responses`` intended for end-to-end request-response
    testing. Automatically knows how to respond to the StaticCompanyMiddleware
    query for the current company, and to static data requests.

    """
    new_dict = COMMON_RESPONSES.copy()
    new_dict.update(response_dict)
    return setup_responses(http, new_dict)



@contextmanager
def locmem_cache():
    cache = get_cache("django.core.cache.backends.locmem.LocMemCache")
    cache.clear()
    patcher = patch("tcmui.core.cache.cache", cache)
    patcher.start()
    yield cache
    patcher.stop()



class CachingFunctionalTestMixin(object):
    def setUp(self):
        self.cache = get_cache("django.core.cache.backends.locmem.LocMemCache")
        self.cache.clear()
        self.patcher = patch("tcmui.core.cache.cache", self.cache)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)



class AuthTestCase(TestCase):
    def creds(self, email, password=None, cookie=None):
        from tcmui.users.auth import UserCredentials
        from tcmui.users.models import User
        creds = UserCredentials(email, password=password, cookie=cookie)
        creds._user = User(email=email)
        creds._permission_codes = []
        return creds


    @property
    def auth(self):
        """
        Since the server responses are mocked, we could just ignore auth when
        not testing it specifically, but we include it for all requests to more
        closely match real usage.

        """
        return self.creds("admin@example.com", cookie="USERTOKEN: authcookie")



class ViewTestCase(AuthTestCase):
    factory = RequestFactory()


    def setUp(self):
        self.rendered = {}
        on_template_render = partial(store_rendered_templates, self.rendered)
        template_rendered.connect(on_template_render)
        self.addCleanup(template_rendered.disconnect, on_template_render)


    def setup_responses(self, http, response_dict):
        setup_common_responses(http, response_dict)


    @property
    def view(self):
        raise NotImplementedError


    def get(self, *args, **kwargs):
        req = self.factory.get(*args, **kwargs)
        req.auth = self.auth
        return self.view(req)



class ResourceTestCase(AuthTestCase):
    @property
    def resource_class(self):
        if not hasattr(self, "_resource_class"):
            self._resource_class = self.get_resource_class()

        return self._resource_class


    def get_resource_class(self):
        raise NotImplementedError


    @property
    def resource_list_class(self):
        if not hasattr(self, "_resource_list_class"):
            self._resource_list_class = self.get_resource_list_class()

        return self._resource_list_class


    def get_resource_list_class(self):
        raise NotImplementedError



class TestResourceTestCase(ResourceTestCase):
    builder = ListBuilder(
        "testresource",
        "testresources",
        "Testresource",
        { "name": "Default name" })


    def get_resource_class(self):
        from tcmui.core.api import RemoteObject, fields

        class TestResource(RemoteObject):
            name = fields.Field()
            submit_as = fields.Field(api_name="submitAs")

            cache = False

            def __unicode__(self):
                return u"__unicode__ of %s" % self.name

        return TestResource


    def get_resource_list_class(self):
        from tcmui.core.api import ListObject, fields

        class TestResourceList(ListObject):
            entryclass = self.resource_class
            api_name = "testresources"
            default_url = "testresources"

            entries = fields.List(fields.Object(self.resource_class))

            cache = False

        return TestResourceList



class BaseResourceTest(object):
    """
    Generic smoke tests that will be run for all resource types.

    """
    pass



class Url(object):
    """
    A wrapper class for comparing urls with querystrings while avoiding
    dict-ordering dependencies. Order of keys in querystring should not matter,
    although order of multiple values for a single key does matter.

    """
    def __init__(self, url):
        self.url = url
        parts = urlparse.urlparse(url)
        self.non_qs = (
            parts.scheme,
            parts.netloc,
            parts.path,
            parts.params,
            parts.fragment)
        # convert values from lists to tuples for hashability later
        self.qs = tuple(sorted((k, tuple(v)) for k, v
                               in urlparse.parse_qs(parts.query).iteritems()))


    def __eq__(self, other):
        return (self.non_qs == other.non_qs) and (self.qs == other.qs)


    def __hash__(self):
        return hash((self.non_qs, self.qs))


    def __repr__(self):
        return "Url(%s)" % self.url
