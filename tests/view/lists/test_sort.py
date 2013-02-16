"""
Tests for sorting utilities.

"""
from mock import Mock

from django.template.response import TemplateResponse
from django.test import RequestFactory

from tests import case

from ...utils import Url



class SortDecoratorTest(case.DBTestCase):
    @property
    def sort(self):
        """The decorator factory under test."""
        from moztrap.view.lists.sort import sort
        return sort


    def on_response(self, response, decorator=None, request=None):
        """Apply given decorator to dummy view, return given response."""
        decorator = decorator or self.sort("ctx_name")
        request = request or RequestFactory().get("/")

        @decorator
        def view(request):
            return response

        return view(request)


    def on_template_response(self, context, **kwargs):
        """Run TemplateResponse with given context through decorated view."""
        request = kwargs.setdefault("request", RequestFactory().get("/"))

        res = TemplateResponse(request, "some/template.html", context)

        return self.on_response(res, **kwargs)


    def test_returns_non_template_response(self):
        """Returns a non-TemplateResponse unmodified, without error."""
        res = self.on_response("blah")

        self.assertEqual(res, "blah")


    def test_uses_wraps(self):
        """Preserves docstring and name of original view func."""
        @self.sort("ctx_name")
        def myview(request, some_id):
            """docstring"""

        self.assertEqual(myview.func_name, "myview")
        self.assertEqual(myview.func_doc, "docstring")


    def test_passes_on_args(self):
        """Arguments are passed on to original view func."""
        record = []

        @self.sort("ctx_name")
        def myview(request, *args, **kwargs):
            record.extend([args, kwargs])

        myview(RequestFactory().get("/"), "a", b=2)

        self.assertEqual(record, [("a",), {"b": 2}])


    def test_orders_queryset(self):
        """Orders queryset in context according to sort params."""
        req = RequestFactory().get(
            "/a/url", {"sortfield": "name", "sortdirection": "asc"})
        qs = Mock()
        self.on_template_response({"ctx_name": qs}, request=req)

        qs.order_by.assert_called_with("name")


    def test_bad_sort_field(self):
        """Silently ignores bad sort field."""
        req = RequestFactory().get(
            "/a/url", {"sortfield": "foo", "sortdirection": "asc"})
        from moztrap.model.core.models import Product  # has no "foo" field

        qs = Product.objects.all()
        res = self.on_template_response({"ctx_name": qs}, request=req)

        self.assertEqual(list(res.context_data["ctx_name"]), [])


    def test_no_sort(self):
        """Handles lack of querystring sort params."""
        qs = Mock()
        self.on_template_response({"ctx_name": qs})

        qs.order_by.assert_called_with("-created_on")


    def test_sort_defaults(self):
        """Decorator factory accepts default sort field and direction."""
        dec = self.sort(
            "ctx_name", defaultfield="name", defaultdirection="desc")
        qs = Mock()
        self.on_template_response({"ctx_name": qs}, decorator=dec)

        qs.order_by.assert_called_with("-name")


    def test_sort_object_in_context(self):
        """Places Sort object in context as "sort"."""
        req = RequestFactory().get(
            "/a/url", {"sortfield": "name", "sortdirection": "desc"})
        res = self.on_template_response({"ctx_name": Mock()}, request=req)

        sort = res.context_data["sort"]
        self.assertEqual(sort.field, "name")
        self.assertEqual(sort.direction, "desc")



class SortTest(case.TestCase):
    def cls(self, full_path, GET):
        """Construct mock request; instantiate and return Sort object."""
        request = Mock()
        request.GET = GET
        request.get_full_path.return_value = full_path

        from moztrap.view.lists.sort import Sort
        return Sort(request)


    def test_attribute_defaults(self):
        """Sort defaults to descending last-modified date."""
        s = self.cls("path", {})

        self.assertEqual(s.field, "created_on")
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
        self.assertEqual(s.order_by, ("-name",))


    def test_order_by_asc(self):
        """order_by property returns "field" for ascending sort on "field"."""
        s = self.cls("path", {"sortfield": "name", "sortdirection": "asc"})
        self.assertEqual(s.order_by, ("name",))


    def test_order_by_multiple_desc(self):
        """order_by property prepends - to each field if multiple."""
        s = self.cls("path", {"sortfield": "one,two", "sortdirection": "desc"})
        self.assertEqual(s.order_by, ("-one", "-two"))


    def test_order_by_multiple_asc(self):
        """order_by property splits field by comma and returns multiple."""
        s = self.cls("path", {"sortfield": "one,two", "sortdirection": "asc"})
        self.assertEqual(s.order_by, ("one", "two"))
