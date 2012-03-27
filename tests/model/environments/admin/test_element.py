"""
Tests for Element admin.

"""
from tests import case



class ElementAdminTest(case.admin.AdminTestCase):
    app_label = "environments"
    model_name = "element"


    def test_changelist(self):
        """Element changelist page loads without error, contains name."""
        self.F.ElementFactory.create(name="Linux")

        self.get(self.changelist_url).mustcontain("Linux")


    def test_change_page(self):
        """Element change page loads without error, contains name."""
        e = self.F.ElementFactory.create(name="Linux")

        self.get(self.change_url(e)).mustcontain("Linux")
