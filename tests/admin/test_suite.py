from .base import AdminTestCase

from ..library.builders import create_suite



class SuiteAdminTest(AdminTestCase):
    app_label = "library"
    model_name = "suite"


    def test_changelist(self):
        """Suite changelist page loads without error, contains name."""
        create_suite(name="Performance")

        self.get(self.changelist_url).mustcontain("Performance")


    def test_change(self):
        """Suite change page loads without error, contains name."""
        s = create_suite(name="Performance")

        self.get(self.change_url(s)).mustcontain("Performance")
