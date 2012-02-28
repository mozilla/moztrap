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
"""Tests for suite/case importer."""
from tests import case



class ImporterTest(case.DBTestCase):
    """Tests for ``Importer``."""
    def setUp(self):
        """Setup for importer tests; create a product version."""
        self.pv = self.F.ProductVersionFactory.create()


    def import_data(self, case_data):
        """Instantiate ``Importer``, call ``import_data`` and return result."""
        from cc.model.library.importer import Importer
        return Importer().import_data(self.pv, case_data)


    def test_create_caseversion(self):
        """Successful import creates a caseversion with expected values."""
        self.import_data(
            {
                "cases": [
                    {
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}]
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.name, "Foo")
        self.assertEqual(cv.productversion, self.pv)
        self.assertEqual(cv.case.product, self.pv.product)


    def test_result_object(self):
        """Successful import returns a result summary object."""
        result = self.import_data(
            {
                "cases": [
                    {
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}]
                        }
                    ]
                }
            )

        self.assertEqual(result.num_cases, 1)
        self.assertEqual(result.num_suites, 0)
        self.assertEqual(result.warnings, [])


    def test_no_step_warning(self):
        """A case with no steps emits a warning."""


    def test_steps(self):
        """Steps are created with correct instruction and expected values."""

