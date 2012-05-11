"""
Utility base TestCase classes for testing APIs.

"""
from django.core.urlresolvers import reverse

from tests.case.view import WebTest
from moztrap.model import API_VERSION


class ApiTestCase(WebTest):


    def get_resource_url(self, url_name, resource_name, params={}):
        kwargs = {
            "resource_name": resource_name,
            "api_name": API_VERSION,
            }
        kwargs.update(params)
        return  reverse(url_name, kwargs=kwargs)


    def get_list_url(self, resource_name):
        return self.get_resource_url("api_dispatch_list", resource_name)


    def get_detail_url(self, resource_name, id):
        return self.get_resource_url(
            "api_dispatch_detail",
            resource_name,
            {"pk": id},
            )


    def get(self, url, params={}):
        params["format"] ="json"
        return self.app.get(url, params=params)


    def get_list(self, params={}):
        return self.get(self.get_list_url(self.resource_name), params)


    def get_detail(self, id, params={}):
        return self.get(self.get_detail_url(self.resource_name, id), params)


    def get_detail_uri(self, resource_name, id):
        url = self.get_detail_url(resource_name, id)
        return "/{0}".format(url.split("/", 1)[1])