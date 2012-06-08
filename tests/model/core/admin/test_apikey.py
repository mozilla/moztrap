"""
Tests for ApiKey admin.

"""
from tests import case



class ApiKeyAdminTest(case.admin.AdminTestCase):
    app_label = "core"
    model_name = "apikey"


    def test_changelist(self):
        """ApiKey changelist page loads without error, contains key."""
        self.F.ApiKeyFactory.create(key="Test API Key")

        self.get(self.changelist_url).mustcontain("Test API Key")


    def test_change_page(self):
        """ApiKey change page loads without error, contains key."""
        k = self.F.ApiKeyFactory.create(key="Test API Key")

        self.get(self.change_url(k)).mustcontain("Test API Key")
