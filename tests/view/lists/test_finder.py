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
Tests for finder.

"""
from django.template.response import TemplateResponse
from django.test import RequestFactory

from mock import Mock, patch

from tests import case



class FinderDecoratorTest(case.DBTestCase):
    """Tests for the finder view decorator."""
    @property
    def finder(self):
        """The decorator under test."""
        from cc.view.lists.decorators import finder
        return finder


    def on_response(self, response, decorator=None, request=None):
        """Apply given decorator to dummy view, return given response."""
        decorator = decorator or self.finder(Mock())
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
        @self.finder(Mock())
        def myview(request, some_id):
            """docstring"""

        self.assertEqual(myview.func_name, "myview")
        self.assertEqual(myview.func_doc, "docstring")


    def test_passes_on_args(self):
        """Arguments are passed on to original view func."""
        record = []

        @self.finder(Mock())
        def myview(request, *args, **kwargs):
            record.extend([args, kwargs])

        myview(RequestFactory().get("/"), "a", b=2)

        self.assertEqual(record, [("a",), {"b": 2}])


    @patch("cc.view.lists.finder.render")
    def test_ajax(self, render):
        """Ajax response is rendered column template."""
        render.return_value = "some HTML"

        MockFinder = Mock()
        f = MockFinder.return_value
        f.column_template.return_value = "some/finder/_column.html"
        f.objects.return_value = ["some", "objects"]

        req = RequestFactory().get(
            "/some/url",
            {"finder": "1", "col": "things", "id": "2"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        res = self.on_template_response(
            {}, request=req, decorator=self.finder(MockFinder))

        self.assertEqual(res, "some HTML")

        self.assertEqual(
            render.call_args[0][1:],
            (
                "some/finder/_column.html",
                {
                    "colname": "things",
                    "finder": {
                        "finder": f,
                        "things": ["some", "objects"]
                        }
                    }
                )
            )

        f.column_template.assert_called_with("things")
        f.objects.assert_called_with("things", "2")


    def test_no_ajax(self):
        """Non-ajax response has finder with top-column objects in context."""
        MockFinder = Mock()
        f = MockFinder.return_value
        top_col = Mock()
        top_col.name = "top"
        f.columns = [top_col]
        f.objects.return_value = ["some", "objects"]

        res = self.on_template_response({}, decorator=self.finder(MockFinder))

        self.assertIs(res.context_data["finder"]["finder"], f)
        self.assertEqual(
            res.context_data["finder"]["top"],
            ["some", "objects"]
            )

        f.objects.assert_called_with("top")



class FinderTest(case.DBTestCase):
    """Tests for Finder."""
    @property
    def ManageFinder(self):
        """ManageFinder; a sample finder subclass to exercise Finder."""
        from cc.view.manage.finders import ManageFinder
        return ManageFinder


    def test_columns_by_name(self):
        """Index of columns by name."""
        f = self.ManageFinder()

        self.assertEqual(
            sorted((n, c.name) for (n, c) in f.columns_by_name.items()),
            [
                ("products", "products"),
                ("productversions", "productversions"),
                ("runs", "runs"),
                ("suites", "suites"),
                ]
            )


    def test_parent_columns(self):
        """Maps column name to parent column."""
        f = self.ManageFinder()

        self.assertEqual(
            sorted((n, c.name) for (n, c) in f.parent_columns.items()),
            [
                ("productversions", "products"),
                ("runs", "productversions"),
                ("suites", "runs"),
                ]
            )


    def test_child_columns(self):
        """Maps column name to child column."""
        f = self.ManageFinder()

        self.assertEqual(
            sorted((n, c.name) for (n, c) in f.child_columns.items()),
            [
                ("products", "productversions"),
                ("productversions", "runs"),
                ("runs", "suites")
                ]
            )


    def test_columns_by_model(self):
        """Index of columns by model."""
        f = self.ManageFinder()

        self.assertEqual(
            sorted(
                ((m, c.name) for (m, c) in f.columns_by_model.items()),
                key=lambda o: o[1]
                ),
            [
                (self.model.Product, "products"),
                (self.model.ProductVersion, "productversions"),
                (self.model.Run, "runs"),
                (self.model.Suite, "suites"),
                ]
            )


    def test_column_template(self):
        """Joins finder base template to column template name."""
        f = self.ManageFinder()

        self.assertEqual(f.column_template("runs"), "manage/finder/_runs.html")


    def test_bad_column_name(self):
        """Bad column name raises ValueError."""
        f = self.ManageFinder()

        with self.assertRaises(ValueError):
            f.column_template("doesnotexist")


    def test_goto_url(self):
        """Goto url is manage url for child objects, filtered by parent."""
        f = self.ManageFinder()

        obj = self.model.Suite(pk=2)

        self.assertEqual(f.goto_url(obj), "/manage/cases/?filter-suite=2")


    def test_goto_url_bad_object(self):
        """Goto url returns None if given object from unknown class."""
        f = self.ManageFinder()

        self.assertEqual(f.goto_url(Mock()), None)


    def test_child_column_for_obj(self):
        """Returns child column name for given object."""
        f = self.ManageFinder()

        obj = self.model.Product()

        child_col = f.child_column_for_obj(obj)

        self.assertEqual(child_col, "productversions")


    def test_child_column_for_bad_obj(self):
        """Returns None if obj isn't of a model class in this finder."""
        f = self.ManageFinder()

        child_col = f.child_column_for_obj(Mock())

        self.assertEqual(child_col, None)


    def test_child_column_for_last_obj(self):
        """Returns None if given object from final-column class."""
        f = self.ManageFinder()

        obj = self.model.Suite()

        child_col = f.child_column_for_obj(obj)

        self.assertEqual(child_col, None)


    def test_child_query_url(self):
        """Returns ajax query url for list of child objects in next column."""
        f = self.ManageFinder()

        obj = self.model.Run(pk=5)

        url = f.child_query_url(obj)
        self.assertEqual(url, "?finder=1&col=suites&id=5")


    def test_child_query_url_none(self):
        """Returns None for final column."""
        f = self.ManageFinder()

        obj = self.model.Suite(pk=5)
        url = f.child_query_url(obj)

        self.assertEqual(url, None)


    def test_objects(self):
        """Without parent, objects is just pass-through to column objects."""
        f = self.ManageFinder()

        p = self.F.ProductFactory.create()

        objects = f.objects("products")

        self.assertEqual(list(objects), [p])


    def test_objects_of_parent(self):
        """With parent, objects filters by parent."""
        f = self.ManageFinder()

        pv = self.F.ProductVersionFactory.create()
        self.F.ProductVersionFactory.create()

        objects = f.objects("productversions", pv.product.pk)

        self.assertEqual(list(objects), [pv])


    def test_parent_via_m2m(self):
        """Parent filtering also works via m2m relationship."""
        f = self.ManageFinder()

        rs = self.F.RunSuiteFactory.create()
        self.F.SuiteFactory.create()

        objects = f.objects("suites", rs.run.pk)

        self.assertEqual(list(objects), [rs.suite])


    def test_no_parent_relationship(self):
        """If no relationship to parent model is found, raises ValueError."""
        from cc.view.lists.finder import Finder, Column

        class BadFinder(Finder):
            columns = [
                Column(
                    "products",
                    "_products.html",
                    self.model.Product.objects.all()
                    ),
                Column("runs", "_runs.html", self.model.Run.objects.all()),
                ]

        f = BadFinder()

        with self.assertRaises(ValueError):
            f.objects("runs", 1)


    def test_objects_of_no_parent(self):
        """Passing in parent for top column raises ValueError."""
        f = self.ManageFinder()

        with self.assertRaises(ValueError):
            f.objects("products", 3)


    def test_objects_bad_col(self):
        """Asking for objects of bad column raises ValueError."""
        f = self.ManageFinder()

        with self.assertRaises(ValueError):
            f.objects("doesnotexist")



class ColumnTest(case.DBTestCase):
    """Tests for finder Column."""
    @property
    def column(self):
        from cc.view.lists.finder import Column
        return Column


    def test_objects(self):
        """Objects method is just .all() on given queryset."""
        qs = Mock()
        c = self.column("thing", "_things.html", qs)

        objects = c.objects()

        self.assertIs(objects, qs.all.return_value)


    @patch("cc.view.lists.finder.filter_url")
    def test_goto_url(self, filter_url):
        """goto_url method calls filter_url if goto is given."""
        c = self.column("thing", "_things.html", Mock(), "goto_name")

        obj = Mock()
        url = c.goto_url(obj)

        self.assertIs(url, filter_url.return_value)
        filter_url.assert_called_with("goto_name", obj)


    def test_no_goto_url(self):
        """goto_url method just returns None if no goto is given."""
        c = self.column("thing", "_things.html", Mock())

        url = c.goto_url(Mock())

        self.assertIs(url, None)
