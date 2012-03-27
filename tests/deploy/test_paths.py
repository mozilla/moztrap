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
