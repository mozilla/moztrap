from unittest2 import TestCase

from .responses import response



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
    return value of the httplib2.Http.request method)."""
    def request(*args, **kwargs):
        uri = kwargs["uri"]
        try:
            return response_dict[uri]
        except KeyError:
            return response(500, "Mock got unexpected request URI: %s" % uri)

    http.request.side_effect = request



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
