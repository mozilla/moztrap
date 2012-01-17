# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Tests for sorting utilities.

"""
from mock import Mock

from django.template.response import TemplateResponse
from django.test import RequestFactory
from django.utils.unittest import TestCase

from ..utils import Url



class SortDecoratorTest(TestCase):
    @property
    def factory(self):
        """Decorator factory."""
        from cc.core.sort import sort
        return sort


    factory_args = ("ctx_name",)


    @property
    def ctx_name(self):
        return self.factory_args[0]


    @property
    def decorator(self):
        """Actual decorator (provides simplest-case args to factory)."""
        return self.factory(*self.factory_args)


    def req(self, method="GET", path="/some/url", *args, **kwargs):
        """Return a request with given method, path, etc."""
        return getattr(RequestFactory(), method.lower())(path, *args, **kwargs)


    def on_response(self, response, decorator=None, request=None):
        """Apply given decorator to dummy view, return given response."""
        decorator = decorator or self.decorator
        request = request or self.req()

        @decorator
        def view(request):
            try:
                response.request = request
            except AttributeError:
                pass
            return response

        return view(request)


    def on_template_response(self, context, **kwargs):
        """Run TemplateResponse with given context through decorated view."""
        request = kwargs.setdefault("request", self.req())

        res = TemplateResponse(request, "some/template.html", context)

        return self.on_response(res, **kwargs)


    def test_returns_non_template_response(self):
        """Returns a non-TemplateResponse unmodified, without error."""
        res = self.on_response("blah")

        self.assertEqual(res, "blah")


    def test_uses_wraps(self):
        """Preserves docstring and name of original view func."""
        @self.decorator
        def myview(request, some_id):
            """docstring"""

        self.assertEqual(myview.func_name, "myview")
        self.assertEqual(myview.func_doc, "docstring")


    def test_passes_on_args(self):
        """Arguments are passed on to original view func."""
        record = []

        @self.decorator
        def myview(request, *args, **kwargs):
            record.extend([args, kwargs])

        myview(self.req(), "a", b=2)

        self.assertEqual(record, [("a",), {"b": 2}])


    def test_orders_queryset(self):
        """Orders queryset in context according to sort params."""
        req = self.req(
            "GET", "/a/url", {"sortfield": "name", "sortdirection": "asc"})
        qs = Mock()
        self.on_template_response({self.ctx_name: qs}, request=req)

        qs.order_by.assert_called_with("name")


    def test_no_sort(self):
        """Handles lack of querystring sort params."""
        qs = Mock()
        self.on_template_response({self.ctx_name: qs})

        qs.order_by.assert_called_with("-modified_on")


    def test_sort_defaults(self):
        """Decorator factory accepts default sort field and direction."""
        dec = self.factory(
            *self.factory_args, defaultfield="name", defaultdirection="desc")
        qs = Mock()
        self.on_template_response({self.ctx_name: qs}, decorator=dec)

        qs.order_by.assert_called_with("-name")


    def test_sort_object_in_context(self):
        """Places Sort object in context as "sort"."""
        req = self.req(
            "GET", "/a/url", {"sortfield": "name", "sortdirection": "desc"})
        res = self.on_template_response({self.ctx_name: Mock()}, request=req)

        sort = res.context_data["sort"]
        self.assertEqual(sort.field, "name")
        self.assertEqual(sort.direction, "desc")



class TestSort(TestCase):
    def cls(self, full_path, GET):
        """Construct mock request; instantiate and return Sort object."""
        request = Mock()
        request.GET = GET
        request.get_full_path.return_value = full_path

        from cc.core.sort import Sort
        return Sort(request)


    def test_attribute_defaults(self):
        """Sort defaults to descending last-modified date."""
        s = self.cls("path", {})

        self.assertEqual(s.field, "modified_on")
        self.assertEqual(s.direction, "desc")


    def test_default_direction(self):
        """For any specified field, sort direction defaults to ascending."""
        s = self.cls("path", {"sortfield": "name"})
        self.assertEqual(s.field, "name")
        self.assertEqual(s.direction, "asc")


    def test_attributes(self):
        """Sort class pulls field and direction attrs from request.GET."""
        s = self.cls("path", {"sortfield": "name", "sortdirection": "desc"})
        self.assertEqual(s.field, "name")
        self.assertEqual(s.direction, "desc")


    def test_url_same_field(self):
        """url property returns opposite sort direction for current field."""
        s = self.cls("path", {"sortfield": "name", "sortdirection": "asc"})
        self.assertEqual(
            Url(s.url("name")), Url("path?sortfield=name&sortdirection=desc"))


    def test_url_other_field(self):
        """url property returns default sort direction for any other field."""
        s = self.cls("path", {"sortfield": "name", "sortdirection": "desc"})
        self.assertEqual(
            Url(s.url("status")),
            Url("path?sortfield=status&sortdirection=asc"))


    def test_dir_same_field(self):
        """dir property returns current sort direction for current field."""
        s = self.cls("path", {"sortfield": "name", "sortdirection": "asc"})
        self.assertEqual(s.dir("name"), "asc")


    def test_dir_other_field(self):
        """dir property returns nothing for any other field."""
        s = self.cls("path", {"sortfield": "name", "sortdirection": "desc"})
        self.assertEqual(s.dir("status"), "")


    def test_order_by_desc(self):
        """order_by property return "-field" for descending sort on "field"."""
        s = self.cls("path", {"sortfield": "name", "sortdirection": "desc"})
        self.assertEqual(s.order_by, "-name")


    def test_order_by_asc(self):
        """order_by property returns "field" for ascending sort on "field"."""
        s = self.cls("path", {"sortfield": "name", "sortdirection": "asc"})
        self.assertEqual(s.order_by, "name")
