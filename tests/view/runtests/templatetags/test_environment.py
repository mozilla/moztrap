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
"""Tests for template tags/filters for setting environment to run tests."""
from django.core.urlresolvers import reverse
from django.test import TestCase

from .... import factories as F



class FilterTest(TestCase):
    """Tests for environment-setting template filters."""
    @property
    def environment(self):
        """The templatetag module under test."""
        from cc.view.runtests.templatetags import environment
        return environment


    def test_set_environment_url(self):
        """Returns set-environment url for a run."""
        run = F.RunFactory()

        self.assertEqual(
            self.environment.set_environment_url(run),
            reverse("runtests_environment", kwargs=dict(run_id=run.id)),
            )
