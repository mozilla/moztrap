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
Tests for queryset-filtering.

"""
from mock import Mock

from django.template.response import TemplateResponse
from django.test import RequestFactory, TestCase
from django.utils.datastructures import MultiValueDict

from ... import factories as F


class DecoratorTest(TestCase):
    """Tests for ``filter`` decorator."""
    @property
    def filter(self):
        """The decorator factory under test."""
        return self.filters.filter


    @property
    def filters(self):
        """The filters module."""
        from cc.view.lists import filters
        return filters


    def on_response(self, response, decorator=None, request=None):
        """Apply given decorator to dummy view, return given response."""
        decorator = decorator or self.filter("ctx_name")
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
        @self.filter("ctx_name")
        def myview(request, some_id):
            """docstring"""

        self.assertEqual(myview.func_name, "myview")
        self.assertEqual(myview.func_doc, "docstring")


    def test_passes_on_args(self):
        """Arguments are passed on to original view func."""
        record = []

        @self.filter("ctx_name")
        def myview(request, *args, **kwargs):
            record.extend([args, kwargs])

        myview(RequestFactory().get("/"), "a", b=2)

        self.assertEqual(record, [("a",), {"b": 2}])


    def test_filterset(self):
        """Constructs FilterSet instance and places it in template context."""
        response = self.on_template_response(
            {"ctx_name": Mock()},
            decorator=self.filter("ctx_name", [self.filters.Filter("name")]),
            )

        fs = response.context_data["filters"]
        self.assertIsInstance(fs, self.filters.FilterSet)
        self.assertEqual(list(fs)[0].name, "name")


    def test_filterset_subclass(self):
        """Accepts a FilterSet subclass to use in ``filterset`` argument."""
        class MyFilterSet(self.filters.FilterSet):
            filters = [self.filters.Filter("name")]

        response = self.on_template_response(
            {"ctx_name": Mock()},
            decorator=self.filter("ctx_name", filterset=MyFilterSet),
            )

        fs = response.context_data["filters"]
        self.assertIsInstance(fs, MyFilterSet)
        self.assertEqual(list(fs)[0].name, "name")


    def test_filters_qs(self):
        """Finds queryset in context; runs it through filterset ``filter``."""
        class MockFilterSet(self.filters.FilterSet):
            def filter(self, queryset):
                # simple annotation so we know it passed through here.
                queryset.filtered = True
                return queryset

        response = self.on_template_response({"ctx_name": Mock()})

        qs = response.context_data["ctx_name"]
        self.assertTrue(qs.filtered)



class FilterSetTest(TestCase):
    """Tests for FilterSet."""
    @property
    def filters(self):
        """The module under test."""
        from cc.view.lists import filters
        return filters


    def test_data(self):
        """
        ``self.data`` is plain dict of lists from given MultiValueDict.

        Only keys beginning with the prefix "filter-" are included, and the
        prefix is stripped from the key.

        """
        fs = self.filters.FilterSet(
            [],
            MultiValueDict(
                {
                    "other": ["a", "b"],
                    "filter-one": ["foo"],
                    "filter-two": ["bar", "baz"]
                    }
                )
            )

        self.assertEqual(fs.data, {"one": ["foo"], "two": ["bar", "baz"]})


    def test_prefix_override(self):
        """'filter-' prefix can be changed via 'filter' kwarg."""
        fs = self.filters.FilterSet(
            [],
            MultiValueDict(
                {
                    "other": ["a", "b"],
                    "foo:one": ["foo"],
                    "foo:two": ["bar", "baz"]
                    }
                ),
            prefix="foo:"
            )

        self.assertEqual(fs.data, {"one": ["foo"], "two": ["bar", "baz"]})


    def test_boundfilters(self):
        """``self.boundfilters`` has a BoundFilter for each given Filter."""
        flt = self.filters.Filter("name")
        fs = self.filters.FilterSet([flt], MultiValueDict())

        self.assertEqual(len(fs.boundfilters), 1)
        self.assertIsInstance(fs.boundfilters[0], self.filters.BoundFilter)
        self.assertIs(fs.boundfilters[0].name, "name")


    def test_class_filters(self):
        """Subclasses can provide filters list as class attribute."""
        class MyFilterSet(self.filters.FilterSet):
            filters = [
                self.filters.Filter("name")
                ]

        fs = MyFilterSet([], MultiValueDict())

        self.assertEqual(len(fs.boundfilters), 1)
        self.assertEqual(fs.boundfilters[0].name, "name")


    def test_instantiation_filters_extend_class_filters(self):
        """Filters given at instantiation extend class-attr filters."""
        class MyFilterSet(self.filters.FilterSet):
            filters = [
                self.filters.Filter("one")
                ]

        fs = MyFilterSet([self.filters.Filter("two")], MultiValueDict())

        self.assertEqual([bf.name for bf in fs.boundfilters], ["one", "two"])


    def test_extend_doesnt_alter_class_attr(self):
        """Providing filters at instantiation doesn't alter the class attr."""
        class MyFilterSet(self.filters.FilterSet):
            filters = [
                self.filters.Filter("one")
                ]

        MyFilterSet([self.filters.Filter("two")], MultiValueDict())
        fs = MyFilterSet([], MultiValueDict())

        self.assertEqual(len(fs.boundfilters), 1)


    def test_iteration_yields_boundfilters(self):
        """Iterating over a FilterSet yields its BoundFilters."""
        fs = self.filters.FilterSet(
            [self.filters.Filter("name")], MultiValueDict())

        self.assertEqual(list(fs), fs.boundfilters)


    def test_len_is_number_of_boundfilters(self):
        """Length of a FilterSet is its number of BoundFilters."""
        class MyFilterSet(self.filters.FilterSet):
            filters = [
                self.filters.Filter("one")
                ]

        fs = MyFilterSet([self.filters.Filter("two")], MultiValueDict())

        self.assertEqual(len(fs), 2)


    def test_filter(self):
        """filter method sends queryset through all filter's filter methods."""
        class MockFilter(self.filters.Filter):
            def filter(self, queryset, values):
                # simple annotation so we can test the qs passed through here
                setattr(queryset, self.name, values)
                return queryset

        fs = self.filters.FilterSet(
            [MockFilter("one"), MockFilter("two")],
            MultiValueDict({"filter-one": ["1"], "filter-two": ["2", "3"]})
            )
        qs = Mock()

        qs = fs.filter(qs)

        self.assertEqual(qs.one, ["1"])
        self.assertEqual(qs.two, ["2", "3"])
