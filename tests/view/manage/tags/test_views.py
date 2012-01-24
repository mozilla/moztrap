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
Tests for tag management views.

"""
from django.core.urlresolvers import reverse

from .... import factories as F
from ...base import ViewTestCase



class TagsAutocompleteTest(ViewTestCase):
    """Test for tags autocomplete view."""
    @property
    def url(self):
        """Shortcut for tag-autocomplete url."""
        return reverse("manage_tags_autocomplete")


    def get(self, query=None):
        """Shortcut for getting tag-autocomplete url authenticated."""
        url = self.url
        if query is not None:
            url = url + "?text=" + query
        return self.app.get(url, user=self.user)


    def test_matching_tags_json(self):
        """Returns list of matching tags in JSON."""
        t = F.TagFactory.create(name="foo")

        res = self.get("o")

        self.assertEqual(
            res.json,
            {
                "suggestions": [
                    {
                        "id": t.id,
                        "name": "foo",
                        "postText": "o",
                        "preText": "f",
                        "type": "tag",
                        "typedText": "o",
                        }
                    ]
                }
            )


    def test_case_insensitive(self):
        """Matching is case-insensitive, but pre/post are case-accurate."""
        t = F.TagFactory.create(name="FooBar")

        res = self.get("oO")

        self.assertEqual(
            res.json,
            {
                "suggestions": [
                    {
                        "id": t.id,
                        "name": "FooBar",
                        "postText": "Bar",
                        "preText": "F",
                        "type": "tag",
                        "typedText": "oO",
                        }
                    ]
                }
            )


    def test_no_query(self):
        """If no query is provided, no tags are returned."""
        F.TagFactory.create(name="foo")

        res = self.get()

        self.assertEqual(res.json, {"suggestions": []})
