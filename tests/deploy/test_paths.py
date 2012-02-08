# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
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
Tests for deployment path-munging functions.

"""
import os.path

from mock import patch

from tests import case



class AddVendorLibTest(case.TestCase):
    """
    Tests for the ``add_vendor_lib`` function.

    """
    def add_vendor_lib(self):
        """Import and call the function."""
        from cc.deploy.paths import add_vendor_lib
        add_vendor_lib()


    def setUp(self):
        """
        Patch sys.path and site.addsitedir so function has no global impact.

        """
        patcher = patch("cc.deploy.paths.sys.path", ["/some/path"])
        self.sys_path = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch("cc.deploy.paths.site.addsitedir")
        self.addsitedir = patcher.start()
        self.addCleanup(patcher.stop)


    def test_calls_addsitedir(self):
        """Calls site.addsitedir on vendor lib dir."""
        vendor_lib = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "requirements", "vendor", "lib", "python"))

        self.add_vendor_lib()

        self.addsitedir.assert_called_with(vendor_lib)


    def test_moves_new_paths_to_front(self):
        """Paths added are moved to front of sys.path."""
        # mock addsitedir as simply adding given path to end of sys.path
        self.addsitedir.side_effect = lambda p: self.sys_path.append(p)

        self.add_vendor_lib()

        # but add_vendor_lib moves it to the beginning
        self.assertEqual(self.sys_path[-1], "/some/path")
