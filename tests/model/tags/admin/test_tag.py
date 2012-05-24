"""
Tests for Tag admin.

"""
from tests import case



class TagAdminTest(case.admin.AdminTestCase):
    app_label = "tags"
    model_name = "tag"


    def test_changelist(self):
        """Tag changelist page loads without error, contains name."""
        self.F.TagFactory.create(name="security")

        self.get(self.changelist_url).mustcontain("security")


    def test_change_page(self):
        """Tag change page loads without error, contains name."""
        p = self.F.TagFactory.create(name="security")

        self.get(self.change_url(p)).mustcontain("security")
