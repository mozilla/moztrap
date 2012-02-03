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
Tests for runtests finder.

"""
from django.test import TestCase

from ... import factories as F



class RunTestsFinderTest(TestCase):
    """Tests for RunTestsFinder."""
    @property
    def finder(self):
        """The Finder class under test."""
        from cc.view.runtests.finders import RunTestsFinder
        return RunTestsFinder


    @property
    def model(self):
        """The models."""
        from cc import model
        return model


    def test_child_query_url(self):
        """child_query_url returns environments URL for a run, not None."""
        f = self.finder()
        r = F.RunFactory.create()

        url = f.child_query_url(r)

        self.assertEqual(
            url, "/runtests/environment/{0}/".format(r.id))


    def test_child_query_url_non_run(self):
        """Given anything but a run, child_query_url defers to Finder."""
        f = self.finder()
        r = F.RunFactory.create()

        url = f.child_query_url(r.productversion)

        self.assertEqual(
            url, "?finder=1&col=runs&id={0}".format(r.productversion.id))
