from contextlib import contextmanager
from functools import partial

from django.core.cache import get_cache
from django.test.signals import template_rendered
from django.test.client import RequestFactory, store_rendered_templates
from mock import patch
from unittest2 import TestCase

from .core.builders import companies
from .responses import response, make_identity



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
    def request(*args, **kwargs):
        uri = kwargs["uri"]
        try:
            return response_dict[uri]
        except KeyError:
            return response(
                {"errors": [
                        {"error": "Mock got unexpected request URI: %s" % uri}
                        ]
                 }
                , 500)

    http.request.side_effect = request


def setup_view_responses(http, response_dict):
    """
    A version of ``setup_responses`` intended for end-to-end request-response
    testing. Automatically knows how to respond to the StaticCompanyMiddleware
    query for the current company.

    """
    response_dict.setdefault(
        "http://fake.base/rest/companies/1?_type=json",
        response(companies.one(
                resourceIdentity=make_identity(id=1, url="companies/1")))
        )
    return setup_responses(http, response_dict)



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
        setup_view_responses(http, response_dict)


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



class BaseResourceTest(object):
    """
    Generic smoke tests that will be run for all resource types.

    """
    pass
