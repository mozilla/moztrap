"""
Utility base TestCase classes for testing APIs.

"""
from django.core.urlresolvers import reverse

from ..base import DBMixin
from tests.case.view import WebTest

from moztrap.model.mtresource import MTModelResource



class ApiTestCase(WebTest):

    def get_resource_url(self, resource_name, id=None):
        url = reverse("api_dispatch_list", kwargs={
            "resource_name": resource_name,
            "api_name": MTModelResource.API_VERSION,
        })

        if id:
            url = "{0}{1}".format(url, str(id))
        return url


