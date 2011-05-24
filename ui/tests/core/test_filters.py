from mock import Mock, patch

from ..responses import make_searchresult, make_list, response
from ..utils import AuthTestCase



class FilterTestCase(AuthTestCase):
    @property
    def status_field_filter(self):
        if not hasattr(self, "_status_field_filter"):
            from tcmui.core.filters import FieldFilter

            class StatusFieldFilter(FieldFilter):
                options = [
                    (1, "draft"),
                    (2, "active"),
                    (3, "locked"),
                     ]

            self._status_field_filter = StatusFieldFilter

        return self._status_field_filter


    def GET(self, **kwargs):
        from django.utils.datastructures import MultiValueDict
        return MultiValueDict(kwargs)


class TestFilter(FilterTestCase):
    @property
    def filter_class(self):
        from tcmui.core.filters import Filter
        return Filter


    def test_field_iteration(self):
        f = self.filter_class(
            self.GET(status=["draft", "active"]),
            self.auth,
            ("status", self.status_field_filter))

        fields = list(f)
        self.assertEqual(len(fields), 1)
        field = fields[0]
        self.assertEqual(field.name, "status")
        self.assertEqual(field.values, set(["draft", "active"]))
        self.assertEqual(field.auth, self.auth)


    def test_filter(self):
        f = self.filter_class(
            self.GET(status=["draft", "active"]),
            self.auth,
            ("status", self.status_field_filter))

        list_obj = Mock()
        f.filter(list_obj)

        list_obj.filter.assert_called_with(status=set(["active", "draft"]))



class FieldFilterTest(FilterTestCase):
    def test_iteration(self):
        ff = self.status_field_filter(
            "status", ["1", "2"])

        options = list(ff)

        self.assertEqual(len(options), 3)
        self.assertEqual([o.value for o in options], [1, 2, 3])
        self.assertEqual(
            [o.label for o in options], ["draft", "active", "locked"])
        self.assertEqual(
            [o.selected for o in options], [True, True, False])

    def test_repr(self):
        ff = self.status_field_filter(
            "status", ["draft", "active"])

        self.assertEqual(
            repr(ff),
            "StatusFieldFilter('status', set(['active', 'draft']))")



class LocatorFieldFilterTest(FilterTestCase):
    @property
    def product_field_filter(self):
        if not hasattr(self, "_product_field_filter"):
            from tcmui.core import fields
            from tcmui.core.api import ListObject, RemoteObject
            from tcmui.core.filters import LocatorFieldFilter

            class Product(RemoteObject):
                name = fields.Field()

                def __unicode__(self):
                    return self.name

            class ProductList(ListObject):
                entryclass = Product
                default_url = "products"
                api_name = "products"

                entries = fields.List(fields.Object(Product))

            class ProductFieldFilter(LocatorFieldFilter):
                target = ProductList

            self._product_field_filter = ProductFieldFilter

        return self._product_field_filter


    @patch("tcmui.core.api.userAgent")
    def test_options(self, http):
        pff = self.product_field_filter("product", self.GET(), self.auth)

        http.request.return_value = response(
            make_searchresult(
                "product", "products", *make_list(
                    "product",
                    "products",
                    {"name": "Product One"},
                    {"name": "Product Two"})))

        options = pff.get_options()

        self.assertEqual(
            options, [(u"1", "Product One"), (u"2", "Product Two")])
        self.assertEqual(
            http.request.call_args[1]["uri"],
            "http://fake.base/rest/products?_type=json")


    @patch("tcmui.core.api.userAgent")
    def test_target_filters(self, http):
        class ActiveProductFieldFilter(self.product_field_filter):
            target_filters = {"name": "Product One"}

        pff = ActiveProductFieldFilter("product", self.GET(), self.auth)

        http.request.return_value = response(
            make_searchresult(
                "product", "products", *make_list(
                    "product",
                    "products",
                    {"name": "Product One"})))

        options = pff.get_options()

        self.assertEqual(
            options, [(u"1", "Product One")])
        self.assertEqual(
            http.request.call_args[1]["uri"],
            "http://fake.base/rest/products?_type=json&name=Product+One")


    @patch("tcmui.core.api.userAgent")
    def test_target_label(self, http):
        class IDProductFieldFilter(self.product_field_filter):
            def target_label(self, obj):
                return obj.id

        pff = IDProductFieldFilter("product", self.GET(), self.auth)

        http.request.return_value = response(
            make_searchresult(
                "product", "products", *make_list(
                    "product",
                    "products",
                    {"name": "Product One"})))

        options = pff.get_options()

        self.assertEqual(
            options, [(u"1", "1")])
