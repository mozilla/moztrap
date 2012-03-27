"""
Tests for Suite admin.

"""
from tests import case



class SuiteAdminTest(case.admin.AdminTestCase):
    app_label = "library"
    model_name = "suite"


    def test_changelist(self):
        """Suite changelist page loads without error, contains name."""
        self.F.SuiteFactory.create(name="Performance")

        self.get(self.changelist_url).mustcontain("Performance")


    def test_change_page(self):
        """Suite change page loads without error, contains name."""
        s = self.F.SuiteFactory.create(name="Performance")

        self.get(self.change_url(s)).mustcontain("Performance")
