"""
Tests for Profile admin.

"""
from tests import case



class ProfileAdminTest(case.admin.AdminTestCase):
    app_label = "environments"
    model_name = "profile"


    def test_changelist(self):
        """Profile changelist page loads without error, contains name."""
        self.F.ProfileFactory.create(name="Browser Environments")

        self.get(self.changelist_url).mustcontain("Browser Environments")


    def test_change_page(self):
        """Profile change page loads without error, contains name."""
        s = self.F.ProfileFactory.create(name="Browser Environments")

        self.get(self.change_url(s)).mustcontain("Browser Environments")
