from unittest2 import TestCase

from .responses import make_one, make_searchresult



class ResourceTestCase(TestCase):
    RESOURCE_DEFAULTS = {}

    RESOURCE_TYPE = ""

    RESOURCE_TYPE_PLURAL = ""


    @property
    def resource_class(self):
        if not hasattr(self, "_resource_class"):
            self._resource_class = self.get_resource_class()

        return self._resource_class


    def get_resource_class(self):
        raise NotImplementedError


    def make_one(self, **kwargs):
        return {
            "ns1.%s" % self.RESOURCE_TYPE: [
                make_one(
                    self.RESOURCE_TYPE,
                    defaults=self.RESOURCE_DEFAULTS,
                    **kwargs)
                ]
            }


    @property
    def resource_list_class(self):
        if not hasattr(self, "_resource_list_class"):
            self._resource_list_class = self.get_resource_list_class()

        return self._resource_list_class


    def get_resource_list_class(self):
        raise NotImplementedError


    def make_searchresult(self, *dicts):
        return make_searchresult(
            self.RESOURCE_TYPE,
            self.RESOURCE_TYPE_PLURAL,
            *[
                make_one(
                    self.RESOURCE_TYPE, defaults=self.RESOURCE_DEFAULTS, **info)
                for info in dicts
                ]
            )


    def creds(self, *args, **kwargs):
        from tcmui.core.auth import Credentials
        return Credentials(*args, **kwargs)


    @property
    def auth(self):
        """
        Since the server responses are mocked, we could just ignore auth when
        not testing it specifically, but we include it for all requests to more
        closely match real usage.

        """
        return self.creds("admin@example.com", cookie="USERTOKEN: authcookie")
