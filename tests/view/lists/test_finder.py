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
from mock import Mock, patch
from unittest2 import TestCase



class FinderTest(TestCase):


    @property
    def finder(self):
        from ccui.core.finder import Finder, Column

        class AFinder(Finder):
            template_base = "a/finder"

            columns = [
                Column("top", "_tops.html", self.TopList, "theTop",
                       goto="list_of_mids"),
                Column("mid", "_mids.html", self.MidList, "theMid"),
                Column("fin", "_fins.html", self.FinList, "theFin")
                ]

        return AFinder


    def test_columns_by_name(self):
        f = self.finder()

        self.assertEqual(
            sorted((n, c.name) for (n, c) in f.columns_by_name.items()),
            [("fin", "fin"), ("mid", "mid"), ("top", "top")]
            )


    def test_parent_columns(self):
        f = self.finder()

        self.assertEqual(
            sorted((n, c.name) for (n, c) in f.parent_columns.items()),
            [("fin", "mid"), ("mid", "top")]
            )


    def test_child_columns(self):
        f = self.finder()

        self.assertEqual(
            sorted((n, c.name) for (n, c) in f.child_columns.items()),
            [("mid", "fin"), ("top", "mid")]
            )


    def test_columns_by_model(self):
        f = self.finder()

        self.assertEqual(
            sorted(
                ((m, c.name) for (m, c) in f.columns_by_model.items()),
                key=lambda o: o[1]
                ),
            [
                (self.Fin, "fin"),
                (self.Mid, "mid"),
                (self.Top, "top"),
                ]
            )


    def test_column_name(self):
        f = self.finder()

        self.assertEqual(f.column_template("mid"), "a/finder/_mids.html")


    def test_bad_column_name(self):
        f = self.finder()

        with self.assertRaises(ValueError):
            f.column_template("doesnotexist")


    @patch("ccui.core.finder.reverse", lambda p: p)
    def test_goto_url(self):
        f = self.finder()

        obj = Mock()
        obj._spec_class = self.Top
        obj.id = 2

        self.assertEqual(f.goto_url(obj), "list_of_mids?theTop=2")


    def test_goto_url_bad_obj(self):
        f = self.finder()

        self.assertEqual(f.goto_url(Mock()), None)


    def test_goto_url_no_goto(self):
        f = self.finder()

        obj = Mock()
        obj._spec_class = self.Mid
        obj.id = 2

        self.assertEqual(f.goto_url(obj), None)


    def test_child_column_for_obj(self):
        f = self.finder()

        obj = Mock()
        obj._spec_class = self.Mid

        child_col = f.child_column_for_obj(obj)

        self.assertEqual(child_col, "fin")


    def test_child_column_for_bad_obj(self):
        f = self.finder()

        child_col = f.child_column_for_obj(Mock())

        self.assertEqual(child_col, None)


    def test_child_column_for_last_obj(self):
        f = self.finder()

        obj = Mock()
        obj._spec_class = self.Fin

        child_col = f.child_column_for_obj(obj)

        self.assertEqual(child_col, None)


    def test_child_query_url(self):
        f = self.finder()

        obj = Mock()
        obj._spec_class = self.Mid
        obj.id = 5

        url = f.child_query_url(obj)
        self.assertEqual(url, "?finder=1&col=fin&id=5")


    def test_child_query_url_none(self):
        f = self.finder()

        obj = Mock()
        obj._spec_class = self.Fin
        obj.id = 5

        url = f.child_query_url(obj)
        self.assertEqual(url, None)


    def test_objects(self):
        f = self.finder()

        objects = f.objects("top")

        our_tops = self.TopList.ours.return_value
        col_tops = our_tops.filter.return_value.sort.return_value

        self.assertIs(objects, col_tops)


    def test_objects_of_parent(self):
        f = self.finder()

        objects = f.objects("mid", 3)

        our_mids = self.MidList.ours.return_value
        col_mids = our_mids.filter.return_value.sort.return_value

        self.assertIs(objects, col_mids.filter.return_value)
        col_mids.filter.assert_called_with(theTop=3)


    def test_objects_of_no_parent(self):
        f = self.finder()

        with self.assertRaises(ValueError):
            f.objects("top", 3)


    def test_objects_bad_col(self):
        f = self.finder()

        with self.assertRaises(ValueError):
            f.objects("doesnotexist")



class ColumnTest(TestCase):
    @property
    def column(self):
        from ccui.core.finder import Column
        return Column


    def test_objects(self):
        ThingList = Mock(name="ThingList")
        c = self.column("thing", "_things.html", ThingList, "theThing")

        objects = c.objects(auth="auth")

        our_things = ThingList.ours.return_value

        self.assertIs(
            objects,
            our_things.filter.return_value.sort.return_value)
        ThingList.ours.assert_called_with(auth="auth")
        our_things.filter.assert_called_with()
        our_things.filter.return_value.sort.assert_called_with("name", "asc")


    def test_custom_sort(self):
        ThingList = Mock(name="ThingList")
        c = self.column(
            "thing", "_things.html", ThingList, "theThing",
            sort=("name", "desc"))

        c.objects(auth="auth")

        our_things = ThingList.ours.return_value

        our_things.filter.return_value.sort.assert_called_with("name", "desc")


    def test_custom_filter(self):
        ThingList = Mock(name="ThingList")
        c = self.column(
            "thing", "_things.html", ThingList, "theThing", prop="value")

        c.objects(auth="auth")

        our_things = ThingList.ours.return_value

        our_things.filter.assert_called_with(prop="value")
