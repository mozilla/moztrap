"""
Utility base TestCase classes for testing APIs.

"""
from django.core.urlresolvers import reverse

from tests.case.view import WebTest
from django_webtest import DjangoTestApp
from moztrap.model import API_VERSION
import urllib
import json



class ApiTestCase(WebTest):


    def get_resource_url(self, url_name, resource_name, params={}):
        kwargs = {
            "resource_name": resource_name,
            "api_name": API_VERSION,
            }
        kwargs.update(params)
        return reverse(url_name, kwargs=kwargs)


    def get_list_url(self, resource_name):
        return self.get_resource_url("api_dispatch_list", resource_name)


    def get_detail_url(self, resource_name, id):
        return self.get_resource_url(
            "api_dispatch_detail",
            resource_name,
            {"pk": id},
            )


    def patch(self, url, payload="", params={}, status=202):
        params.setdefault("format", "json")
        url = "{0}?{1}".format(url, urllib.urlencode(params))
        json_data = json.dumps(payload)
        return self.app.patch(
            url,
            json_data,
            headers = {"content-type": "application/json"},
            status=status,
            )


    def post(self, url, payload="", params={}, status=201):
        params.setdefault("format", "json")
        url = "{0}?{1}".format(url, urllib.urlencode(params))
        json_data = json.dumps(payload)
        return self.app.post(
            url,
            json_data,
            headers = {"content-type": "application/json"},
            status=status,
            )


    def get(self, url, params={}, status=200):
        params.setdefault("format", "json")
        return self.app.get(url, params=params, status=status)


    def get_list(self, params={}, status=200):
        return self.get(
            self.get_list_url(self.resource_name),
            params=params,
            status=status,
            )


    def get_detail(self, id, params={}, status=200):
        return self.get(
            self.get_detail_url(self.resource_name, id),
            params=params,
            status=status,
            )


    def get_detail_uri(self, resource_name, id):
        url = self.get_detail_url(resource_name, id)
        return "/{0}".format(url.split("/", 1)[1])


    def renew_app(self):
        """
        Resets self.app (drops the stored state): cookies, etc.
        Note: this renews only self.app, not the responses fetched by self.app.
        """
        self.app = DjangoAPITestApp(extra_environ=self.extra_environ)


class DjangoAPITestApp(DjangoTestApp):

    def patch(self, url, params='', headers=None, extra_environ=None,
             status=None, upload_files=None, expect_errors=False,
             content_type=None):
        """
        Do a POST request.  Very like the ``.get()`` method.
        ``params`` are put in the body of the request.

        ``upload_files`` is for file uploads.  It should be a list of
        ``[(fieldname, filename, file_content)]``.  You can also use
        just ``[(fieldname, filename)]`` and the file content will be
        read from disk.

        Returns a ``webob.Response`` object.
        """
        return self._gen_request('PATCH', url, params=params, headers=headers,
                                 extra_environ=extra_environ, status=status,
                                 upload_files=upload_files,
                                 expect_errors=expect_errors,
                                 content_type=content_type)
